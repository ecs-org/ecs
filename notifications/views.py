# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.db import models

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.utils.pdfutils import wkhtml2pdf
from ecs.utils.security import readonly
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.core.forms.layout import get_notification_form_tabs
from ecs.core.diff import diff_submission_forms
from ecs.core.models import SubmissionForm, Submission
from ecs.core.parties import get_presenting_parties
from ecs.documents.models import Document
from ecs.tracking.decorators import tracking_hint
from ecs.notifications.models import Notification, NotificationType, NotificationAnswer
from ecs.notifications.forms import NotificationAnswerForm, RejectableNotificationAnswerForm
from ecs.documents.views import upload_document, delete_document
from ecs.audit.utils import get_version_number
from ecs.users.utils import user_flag_required


def _get_notification_template(notification, pattern):
    template_names = [pattern % name for name in (notification.type.form_cls.__name__, 'base')]
    return loader.select_template(template_names)

def _get_notification_download_name(notification, suffix=''):
    ec_num = '_'.join(str(s['ec_number']) for s in Submission.objects.filter(forms__notifications=notification).order_by('ec_number').values('ec_number'))
    return slugify("%s-%s" % (ec_num, notification.type.name)) + suffix

def _notification_pdf_response(notification, tpl_pattern, suffix='.pdf', context=None):
    tpl = _get_notification_template(notification, tpl_pattern)
    html = tpl.render(Context(context or {}))
    pdf = wkhtml2pdf(html)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=%s' % _get_notification_download_name(notification, suffix)
    return response


def _get_notifications(**lookups):
    return Notification.objects.filter(**lookups).annotate(min_ecn=models.Min('submission_forms__submission__ec_number')).order_by('min_ecn')
    
def _notification_list(request, answered=None, stashed=False):
    if answered:
        title = _('Answered Notifications')
        notifications = _get_notifications(answer__isnull=False)
    elif answered is None:
        title = _('All Notifications')
        notifications = _get_notifications()
    else:
        title = _('Open Notifications')
        notifications = _get_notifications(answer__isnull=True)
    context = {
        'title': title, 
        'notifs': notifications,
    }
    if stashed:
        context['stashed_notifications'] = DocStash.objects.filter(group='ecs.notifications.views.create_notification')
    return render(request, 'notifications/list.html', context)


@readonly()
def open_notifications(request):
    return _notification_list(request, answered=False, stashed=True)


@readonly()
def answered_notifications(request):
    return _notification_list(request, answered=True)


@readonly()
def view_notification(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    tpl = _get_notification_template(notification, 'notifications/view/%s.html')
    return render(request, tpl, {
        'documents': notification.documents.exclude(status='deleted').order_by('doctype__identifier', 'version', 'date'),
        'notification': notification,
    })


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
        'notification_types': NotificationType.objects.filter(includes_diff=False).order_by('name')
    })


def create_diff_notification(request, submission_form_pk=None, notification_type_pk=None):
    new_submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, is_notification_update=True)
    old_submission_form = new_submission_form.submission.current_submission_form
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    
    diff = diff_submission_forms(old_submission_form, new_submission_form).html()
    
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
                'diff': diff,
            }
        })
        docstash.name = u"%s für %s" % (notification_type.name, old_submission_form)
    return HttpResponseRedirect(reverse('ecs.notifications.views.create_notification', kwargs={'docstash_key': docstash.key, 'notification_type_pk': notification_type.pk}))


@with_docstash_transaction(group='ecs.notifications.views.create_notification')
def delete_docstash_entry(request):
    for sf in request.docstash.get('submission_forms'):
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
    return HttpResponseRedirect(reverse('ecs.notifications.views.upload_document_for_notification', kwargs={'docstash_key': request.docstash.key}))

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
            'submission_forms': getattr(form, 'cleaned_data', {}).get('submission_forms', []),
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
            return HttpResponseRedirect(reverse('ecs.notifications.views.view_notification', kwargs={'notification_pk': notification.pk}))

    return render(request, 'notifications/form.html', {
        'notification_type': notification_type,
        'form': form,
        'tabs': get_notification_form_tabs(type(form)),
    })


@user_flag_required('is_internal')
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
        #return HttpResponseRedirect(reverse('ecs.notifications.views.view_notification_answer', kwargs={'notification_pk': notification.pk}))
    return render(request, 'notifications/answers/form.html', {
        'notification': notification,
        'answer': answer,
        'answer_version': get_version_number(answer) if answer else 0,
        'form': form,
    })


@readonly()
def view_notification_answer(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk, answer__isnull=False)
    return render(request, 'notifications/answers/view.html', {
        'notification': notification,
        'answer': notification.answer,
    })
    

@readonly()
def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    submission_forms = notification.submission_forms.select_related('submission').all()
    protocol_numbers = [sf.protocol_number for sf in submission_forms if sf.protocol_number]
    protocol_numbers.sort()
    return _notification_pdf_response(notification, 'db/notifications/wkhtml2pdf/%s.html', suffix='.pdf', context={
        'notification': notification,
        'protocol_numbers': protocol_numbers,
        'submission_forms': submission_forms,
        'documents': notification.documents.select_related('doctype').order_by('doctype__name', 'version', 'date'),
        'url': request.build_absolute_uri(),
    })


@readonly()
def notification_answer_pdf(request, notification_pk=None):
    answer = get_object_or_404(NotificationAnswer, notification__pk=notification_pk)
    return _notification_pdf_response(answer.notification, 'db/notifications/answers/wkhtml2pdf/%s.html', suffix='-answer.pdf', context={
        'notification': answer.notification,
        'documents': answer.notification.documents.select_related('doctype').order_by('doctype__name', 'version', 'date'),
        'answer': answer,
    })
