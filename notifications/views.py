# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.documents.models import Document
from ecs.core.forms.layout import get_notification_form_tabs
from ecs.utils.pdfutils import xhtml2pdf
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.core.forms import DocumentForm
from ecs.core.diff import diff_submission_forms

from ecs.core.models import SubmissionForm, Investigator, Submission
from ecs.notifications.models import Notification, NotificationType

# notifications
def notification_list(request):
    return render(request, 'notifications/list.html', {
        'notifications': Notification.objects.all(),
        'stashed_notifications': DocStash.objects.filter(group='ecs.notifications.views.create_notification'),
    })

def view_notification(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    template_names = ['notifications/view/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    return render(request, template_names, {
        'documents': notification.documents.filter(deleted=False).order_by('doctype__name', '-date'),
        'notification': notification,
    })
    
def submission_data_for_notification(request):
    submission_forms = list(SubmissionForm.objects.filter(pk__in=request.GET.getlist('submission_form')))
    return render(request, 'notifications/submission_data.html', {
        'submission_forms': submission_forms,
    })

def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.exclude(diff=True).order_by('name')
    })
    

def create_diff_notification(request, submission_form_pk=None, notification_type_pk=None):
    new_submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk, is_notification_update=True)
    old_submission_form = new_submission_form.submission.current_submission_form
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    
    tpl = loader.get_template('submissions/diff/diff.inc.html')
    diff = tpl.render(Context({
        'diffs': diff_submission_forms(old_submission_form, new_submission_form),
    }))
    
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


@with_docstash_transaction
def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash.get('form')
    else:
        form = notification_type.form_cls(request.POST or None)

    doc_post = 'document-file' in request.FILES
    document_form = DocumentForm(request.POST if doc_post else None, request.FILES if doc_post else None, 
        document_pks=[x.pk for x in request.docstash.get('documents', [])], 
        prefix='document'
    )
    
    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        autosave = request.POST.get('autosave', False)
        
        request.docstash.update({
            'form': form,
            'type_id': notification_type_pk,
            'documents': list(Document.objects.filter(pk__in=map(int, request.POST.getlist('documents')))),
            'submission_forms': getattr(form, 'cleaned_data', {}).get('submission_forms', []),
        })
        request.docstash.name = "%s" % notification_type.name
        
        if autosave:
            return HttpResponse(_('autosave successful'))
        
        if document_form.is_valid():
            documents = set(request.docstash['documents'])
            documents.add(document_form.save())
            replaced_documents = [x.replaces_document for x in documents if x.replaces_document]
            for doc in replaced_documents:  # remove replaced documents
                if doc in documents:
                    documents.remove(doc)
            request.docstash['documents'] = list(documents)
            document_form = DocumentForm(document_pks=[x.pk for x in documents], prefix='document')

        if submit and form.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            for key, value in request.docstash.get('extra', {}).items():
                setattr(notification, key, value)
            notification.save()
            form.save_m2m()
            notification.documents = request.docstash['documents']

            request.docstash.delete()
            return HttpResponseRedirect(reverse('ecs.notifications.views.view_notification', kwargs={'notification_pk': notification.pk}))
        else:
            print form.errors

    return render(request, 'notifications/form.html', {
        'notification_type': notification_type,
        'form': form,
        'tabs': get_notification_form_tabs(type(form)),
        'document_form': document_form,
        'documents': request.docstash.get('documents', []),
    })

def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    template_names = ['db/notifications/xhtml2pdf/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    tpl = loader.select_template(template_names)
    html = tpl.render(Context({
        'notification': notification,
        'url': request.build_absolute_uri(),
    }))
    pdf = xhtml2pdf(html)
    ec_num = '_'.join(str(s['ec_number']) for s in Submission.objects.filter(forms__notifications=notification).order_by('ec_number').values('ec_number'))
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=%s.pdf' % slugify("%s-%s" % (ec_num, notification.type.name))
    return response

