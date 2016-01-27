from uuid import uuid4

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.db import models

from ecs.utils.viewutils import render_html, render_pdf, redirect_to_next_url
from ecs.utils.security import readonly
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.core.forms.layout import get_notification_form_tabs
from ecs.core.models import SubmissionForm
from ecs.documents.models import Document
from ecs.tracking.decorators import tracking_hint
from ecs.notifications.models import Notification, NotificationType, NotificationAnswer
from ecs.notifications.forms import NotificationAnswerForm, RejectableNotificationAnswerForm
from ecs.notifications.signals import on_notification_submit
from ecs.documents.views import handle_download, upload_document, delete_document
from ecs.users.utils import user_flag_required, user_group_required
from ecs.tasks.utils import task_required, with_task_management
from ecs.signature.views import init_batch_sign


def _get_notification_template(notification, pattern):
    template_names = [pattern % name for name in (notification.type.form_cls.__name__, 'base')]
    return loader.select_template(template_names)

@readonly()
def open_notifications(request):
    title = _('Open Notifications')
    notifications =  Notification.objects.pending().annotate(min_ecn=models.Min('submission_forms__submission__ec_number')).order_by('min_ecn')
    stashed_notifications = DocStash.objects.filter(
        owner=request.user, group='ecs.notifications.views.create_notification')
    context = {
        'title': title,
        'notifs': notifications,
        'stashed_notifications': stashed_notifications,
    }
    return render(request, 'notifications/list.html', context)


@readonly()
@with_task_management
def view_notification(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    tpl = _get_notification_template(notification, 'notifications/view/%s.html')
    return HttpResponse(tpl.render({
        'documents': notification.documents.order_by('doctype__identifier', 'version', 'date'),
        'notification': notification,
    }, request))


@readonly()
def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    return handle_download(request, notification.pdf_document)


@readonly()
def download_document(request, notification_pk=None, document_pk=None, view=False):
    notification = get_object_or_404(Notification, pk=notification_pk)
    document = get_object_or_404(notification.documents, pk=document_pk)
    return handle_download(request, document, view=view)


@readonly()
def view_document(request, notification_pk=None, document_pk=None):
    return download_document(request, notification_pk, document_pk, view=True)


@readonly()
def submission_data_for_notification(request):
    pks = [pk for pk in request.GET.getlist('submission_form') if pk]
    submission_forms = list(SubmissionForm.objects.filter(pk__in=pks))
    return render(request, 'notifications/submission_data.html', {
        'submission_forms': submission_forms,
    })


@readonly()
def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.filter(includes_diff=False).order_by('position')
    })


def create_diff_notification(request, submission_form_pk=None, notification_type_pk=None):
    new_submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, is_notification_update=True)
    old_submission_form = new_submission_form.submission.current_submission_form
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    
    docstash = DocStash.objects.create(group='ecs.notifications.views.create_notification', owner=request.user)
    
    with docstash.transaction():
        docstash.update({
            'form': notification_type.form_cls(),
            'type_id': notification_type_pk,
            'documents': [],
            'submission_forms': [old_submission_form],
            'extra': {
                'old_submission_form': old_submission_form,
                'new_submission_form': new_submission_form,
            }
        })
        docstash.name = "%s für %s" % (notification_type.name, old_submission_form)
    return redirect('ecs.notifications.views.create_notification', docstash_key=docstash.key, notification_type_pk=notification_type.pk)


@with_docstash_transaction(group='ecs.notifications.views.create_notification')
def delete_docstash_entry(request):
    for sf in request.docstash.get('submission_forms', []):
        if sf.is_notification_update:
            sf.delete()
    request.docstash.delete()
    return redirect_to_next_url(request, reverse('ecs.dashboard.views.view_dashboard'))

@with_docstash_transaction(group='ecs.notifications.views.create_notification')
def upload_document_for_notification(request):
    return upload_document(request, 'notifications/upload_form.html')

@with_docstash_transaction(group='ecs.notifications.views.create_notification')
def delete_document_from_notification(request):
    delete_document(request, int(request.GET['document_pk']))
    return redirect('ecs.notifications.views.upload_document_for_notification', docstash_key=request.docstash.key)

@tracking_hint(vary_on=['notification_type_pk'])
@with_docstash_transaction
def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    request.docstash['type_id'] = notification_type_pk
    
    form = request.docstash.get('form')
    if request.method == 'POST' or form is None:
        form = notification_type.form_cls(request.POST or None)

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        save = request.POST.get('save', False)
        autosave = request.POST.get('autosave', False)
        
        request.docstash.update({
            'form': form,
            'submission_forms': list(SubmissionForm.objects.filter(pk__in=form.data.getlist('submission_forms'))), # we cannot use cleaned_data as the form may not validate
        })
        request.docstash.name = "%s" % notification_type.name
        
        if save or autosave:
            return HttpResponse(_('save successful'))
        
        if submit and form.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            notification.user = request.user
            for key, value in request.docstash.get('extra', {}).items():
                setattr(notification, key, value)
            notification.save()
            form.save_m2m()
            notification.documents = Document.objects.filter(pk__in=request.docstash.get('document_pks', []))
            notification.save() # send another post_save signal (required to properly start the workflow)
            request.docstash.delete()
            
            on_notification_submit.send(type(notification), notification=notification)

            return redirect('ecs.notifications.views.view_notification', notification_pk=notification.pk)
            

    return render(request, 'notifications/form.html', {
        'notification_type': notification_type,
        'form': form,
        'tabs': get_notification_form_tabs(type(form)),
    })


@task_required
@with_task_management
def edit_notification_answer(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    kwargs = {}
    try:
        answer = notification.answer
    except NotificationAnswer.DoesNotExist:
        answer = None
        kwargs['initial'] = {'text': notification.type.default_response}
    
    form_cls = NotificationAnswerForm
    if notification.type.is_rejectable:
        form_cls = RejectableNotificationAnswerForm
    
    form = form_cls(request.POST or None, instance=answer, **kwargs)
    task = request.task_management.task
    if task:
        form.bound_to_task = task
    if form.is_valid():
        answer = form.save(commit=False)
        answer.notification = notification
        answer.save()

    response = render(request, 'notifications/answers/form.html', {
        'notification': notification,
        'answer': answer,
        'answer_version': answer.version_number if answer else 0,
        'form': form,
    })
    response.has_errors = not form.is_valid()
    return response


@readonly()
def view_notification_answer(request, notification_pk=None):
    answer = get_object_or_404(NotificationAnswer, notification__pk=notification_pk)
    return render(request, 'notifications/answers/view.html', {
        'notification': answer.notification,
        'answer': answer,
    })


@readonly()
def notification_answer_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    return handle_download(request, notification.answer.pdf_document)
    

@user_flag_required('is_internal')
@user_group_required("EC-Signing Group")
@task_required
def notification_answer_sign(request, notification_pk=None):
    answer = get_object_or_404(NotificationAnswer, notification__pk=notification_pk)
    return init_batch_sign(request, request.related_tasks[0], get_notification_answer_sign_data)

def get_notification_answer_sign_data(request, task):
    answer = task.data.answer
    pdf_template = answer.notification.type.get_template('notifications/answers/wkhtml2pdf/%s.html')
    html_template = pdf_template    # FIXME
    context = answer.get_render_context()
    return {
        'success_func': sign_success,
        'parent_pk': answer.pk,
        'parent_type': NotificationAnswer,
        'document_uuid': uuid4().hex,
        'document_name': answer.notification.get_filename('-answer'),
        'document_type': "notification_answer",
        'document_version': 'signed-at',
        'document_filename': answer.notification.get_filename('-answer.pdf'),
        'document_barcodestamp': True,
        'html_preview': render_html(request, html_template, context),
        'pdf_data': render_pdf(request, pdf_template, context),
    }

def sign_success(request, document=None):
    answer = document.parent_object
    answer.signed_at = document.date
    answer.pdf_document = document
    answer.save()
    return reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': answer.notification.pk})