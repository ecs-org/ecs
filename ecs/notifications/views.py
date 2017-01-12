from uuid import uuid4

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.db.models import Min, Q, Prefetch

from ecs.utils.viewutils import render_html, redirect_to_next_url
from ecs.docstash.decorators import with_docstash
from ecs.docstash.models import DocStash
from ecs.core.forms.layout import get_notification_form_tabs
from ecs.core.models import SubmissionForm, Investigator
from ecs.documents.models import Document
from ecs.notifications.models import (
    Notification, NotificationType, NotificationAnswer, CenterCloseNotification,
)
from ecs.notifications.forms import (
    NotificationAnswerForm, RejectableNotificationAnswerForm,
    AmendmentAnswerForm,
)
from ecs.documents.views import handle_download, upload_document, delete_document
from ecs.users.utils import user_group_required
from ecs.tasks.utils import task_required, with_task_management
from ecs.signature.views import init_batch_sign


def _get_notification_template(notification, pattern):
    template_names = [pattern % name for name in (notification.type.form_cls.__name__, 'base')]
    return loader.select_template(template_names)

def open_notifications(request):
    title = _('Open Notifications')
    notifications = (Notification.objects
        .pending()
        .annotate(min_ecn=Min('submission_forms__submission__ec_number'))
        .select_related('safetynotification', 'type')
        .prefetch_related(Prefetch('submission_forms',
            queryset=SubmissionForm.objects
                .select_related('submission')
                .order_by('submission__ec_number')))
        .order_by('min_ecn')
    )
    stashed_notifications = DocStash.objects.filter(
        owner=request.user, group='ecs.notifications.views.create_notification',
        current_version__gte=0
    ).order_by('-modtime')
    context = {
        'title': title,
        'notifs': notifications,
        'stashed_notifications': stashed_notifications,
    }
    return render(request, 'notifications/list.html', context)


@with_task_management
def view_notification(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    tpl = _get_notification_template(notification, 'notifications/view/%s.html')
    return HttpResponse(tpl.render({
        'documents': notification.documents.order_by('doctype__identifier', 'date', 'name'),
        'notification': notification,
        'answer': getattr(notification, 'answer', None),
    }, request))


def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    return handle_download(request, notification.pdf_document)


def notification_pdf_debug(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    response = HttpResponse(notification.render_pdf(),
        content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=debug.pdf'
    return response


def download_document(request, notification_pk=None, document_pk=None, view=False):
    notification = get_object_or_404(Notification, pk=notification_pk)
    document = get_object_or_404(notification.documents, pk=document_pk)
    return handle_download(request, document, view=view)


def view_document(request, notification_pk=None, document_pk=None):
    return download_document(request, notification_pk, document_pk, view=True)


def submission_data_for_notification(request):
    pks = [pk for pk in request.GET.getlist('submission_form') if pk]
    submission_forms = list(SubmissionForm.objects.filter(pk__in=pks))
    return render(request, 'notifications/submission_data.html', {
        'submission_forms': submission_forms,
    })


def investigators_for_notification(request):
    submission_form = get_object_or_404(SubmissionForm, pk=request.GET['submission_form'])

    investigators = submission_form.investigators.all()

    closed_investigators = Investigator.objects.filter(
        submission_form__submission_id=submission_form.submission.id,
        id__in=CenterCloseNotification.objects.filter(
            Q(answer__published_at=None) |
            Q(answer__published_at__isnull=False, answer__is_rejected=False)
        ).values('investigator_id')
    ).values('organisation', 'ethics_commission_id')

    for inv in closed_investigators:
        investigators = investigators.exclude(
            organisation=inv['organisation'],
            ethics_commission_id=inv['ethics_commission_id']
        )

    return render(request, 'notifications/investigators.html', {
        'investigators': investigators,
    })


def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.filter(includes_diff=False).order_by('position')
    })


def create_diff_notification(request, submission_form_pk=None, notification_type_pk=None):
    new_submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, is_notification_update=True)
    old_submission_form = new_submission_form.submission.current_submission_form
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    
    docstash = DocStash.objects.create(
        group='ecs.notifications.views.create_notification',
        name='{} für {}'.format(notification_type.name, old_submission_form),
        owner=request.user,
        value={
            'type_id': notification_type_pk,
            'submission_form_ids': [old_submission_form.id],
            'extra': {
                'old_submission_form_id': old_submission_form.id,
                'new_submission_form_id': new_submission_form.id,
            }
        }
    )

    return redirect('ecs.notifications.views.create_notification',
        docstash_key=docstash.key, notification_type_pk=notification_type.pk)


@with_docstash(group='ecs.notifications.views.create_notification')
def delete_docstash_entry(request):
    for sf in request.docstash.get('submission_forms', []):
        if sf.is_notification_update:
            sf.delete()
    request.docstash.delete()
    return redirect_to_next_url(request, reverse('ecs.dashboard.views.view_dashboard'))

@with_docstash(group='ecs.notifications.views.create_notification')
def upload_document_for_notification(request):
    return upload_document(request, 'notifications/upload_form.html')

@with_docstash(group='ecs.notifications.views.create_notification')
def delete_document_from_notification(request):
    delete_document(request, int(request.GET['document_pk']))
    return redirect('ecs.notifications.views.upload_document_for_notification',
        docstash_key=request.docstash.key)

@with_docstash()
def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    request.docstash['type_id'] = notification_type_pk

    form = notification_type.form_cls(request.POST or request.docstash.POST)

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        save = request.POST.get('save', False)
        autosave = request.POST.get('autosave', False)
        
        if not request.docstash.name:
            request.docstash.name = notification_type.name
        # we cannot use cleaned_data as the form may not validate
        request.docstash['submission_form_ids'] = \
            [int(pk) for pk in form.data.getlist('submission_forms')]
        request.docstash.POST = request.POST
        request.docstash.save()
        
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
            
            notification.render_pdf_document()
            return redirect('ecs.notifications.views.view_notification',
                notification_pk=notification.pk)

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
    if hasattr(notification, 'amendmentnotification'):
        form_cls = AmendmentAnswerForm
    elif notification.type.is_rejectable:
        form_cls = RejectableNotificationAnswerForm
    
    form = form_cls(request.POST or None, instance=answer, **kwargs)
    if form.is_valid():
        answer = form.save(commit=False)
        answer.notification = notification
        answer.save()
        if hasattr(notification, 'amendmentnotification'):
            an = notification.amendmentnotification
            an.is_substantial = form.cleaned_data.get('is_substantial', False)
            an.needs_signature = form.cleaned_data.get('needs_signature', False)
            an.save()

    response = render(request, 'notifications/answers/form.html', {
        'notification': notification,
        'answer': answer,
        'answer_version': answer.version_number if answer else 0,
        'form': form,
    })
    response.has_errors = not form.is_valid()
    return response


def notification_answer_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    return handle_download(request, notification.answer.pdf_document)


def notification_answer_pdf_debug(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    response = HttpResponse(notification.answer.render_pdf(),
        content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=debug.pdf'
    return response
    

@user_group_required("EC-Signing")
@task_required
def notification_answer_sign(request, notification_pk=None):
    answer = get_object_or_404(NotificationAnswer, notification__pk=notification_pk)
    return init_batch_sign(request, request.related_tasks[0], get_notification_answer_sign_data)

def get_notification_answer_sign_data(request, task):
    notification = task.data
    answer = notification.answer
    html_template = notification.type.get_template('notifications/answers/pdf/%s.html')
    context = answer.get_render_context()
    return {
        'success_func': sign_success,
        'parent_pk': answer.pk,
        'parent_type': NotificationAnswer,
        'document_uuid': uuid4().hex,
        'document_name': notification.get_filename('-answer'),
        'document_type': "notification_answer",
        'document_version': 'signed-at',
        'document_filename': notification.get_filename('-answer.pdf'),
        'document_barcodestamp': True,
        'html_preview': render_html(request, html_template, context),
        'pdf_data': answer.render_pdf(),
    }

def sign_success(request, document=None):
    answer = document.parent_object
    answer.signed_at = document.date
    answer.pdf_document = document
    answer.save()
    return reverse('ecs.notifications.views.view_notification', kwargs={'notification_pk': answer.notification.pk})
