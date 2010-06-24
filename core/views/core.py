# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

from ecs.core.views.utils import render, redirect_to_next_url
from ecs.core.models import Document, Notification, NotificationType, SubmissionForm, Investigator, Submission
from ecs.core.forms import DocumentFormSet
from ecs.core.forms.layout import NOTIFICATION_FORM_TABS
from ecs.utils.xhtml2pdf import xhtml2pdf
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash

# documents
def download_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    response = HttpResponse(doc.file, content_type=doc.mimetype)
    response['Content-Disposition'] = 'attachment;filename=document_%s.pdf' % doc.pk
    return response
    
# notifications
def notification_list(request):
    return render(request, 'notifications/list.html', {
        'notifications': Notification.objects.all(),
        'stashed_notifications': DocStash.objects.filter(group='ecs.core.views.core.create_notification'),
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
    investigators = Investigator.objects.filter(submission_form__in=submission_forms)
    return render(request, 'notifications/submission_data.html', {
        'submission_forms': submission_forms,
        'investigators': investigators,
    })

# FIXME: move this into create_notification()
def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.order_by('name')
    })

@with_docstash_transaction
def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash.get('form')
    else:
        form = notification_type.form_cls(request.POST or None)

    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')
    
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
            return HttpResponse('autosave successful')
        
        if document_formset.is_valid():
            request.docstash['documents'] = request.docstash['documents'] + document_formset.save()
            document_formset = DocumentFormSet(prefix='document')
        
        if submit and form.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            notification.save()
            submission_forms = form.cleaned_data['submission_forms']
            notification.submission_forms = submission_forms
            notification.investigators.add(*Investigator.objects.filter(submission_form__in=submission_forms))
            notification.documents = request.docstash['documents']
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))

    return render(request, 'notifications/form.html', {
        'notification_type': notification_type,
        'form': form,
        'tabs': NOTIFICATION_FORM_TABS[form.__class__],
        'document_formset': document_formset,
        'documents': request.docstash.get('documents', []),
    })

def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    template_names = ['notifications/xhtml2pdf/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    tpl = loader.select_template(template_names)
    html = tpl.render(Context({
        'notification': notification,
        'investigators': notification.investigators.order_by('ethics_commission__name', 'name'),
        'url': request.build_absolute_uri(),
    }))
    pdf = xhtml2pdf(html)
    ec_num = '_'.join(s['ec_number'] for s in Submission.objects.filter(forms__notifications=notification).order_by('ec_number').values('ec_number'))
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=%s.pdf' % slugify("%s-%s" % (ec_num, notification.type.name))
    return response

