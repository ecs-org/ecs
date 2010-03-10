# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader, Template
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.forms.models import inlineformset_factory

import settings

from ecs.core.models import Document, BaseNotificationForm, NotificationType, Submission, SubmissionForm
from ecs.core.forms import DocumentFormSet, SubmissionFormForm, MeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.utils.htmldoc import htmldoc
from ecs.core import paper_forms

## helpers

def render(request, template, context):
    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not isinstance(template, Template):
        template = loader.get_template(template)
    return HttpResponse(template.render(RequestContext(request, context)))
    
def redirect_to_next_url(request, default_url=None):
    next = request.REQUEST.get('next')
    if not next or '//' in next:
        next = default_url or '/'
    return HttpResponseRedirect(next)

## views

def demo(request):
    return render_to_response('demo-django.html')

def index(request):
    return render(request, 'index.html', {})

# documents
def download_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    response = HttpResponse(doc.file, content_type=doc.mimetype)
    response['Content-Disposition'] = 'attachment;filename=document_%s.pdf' % doc.pk
    return response
    
def delete_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    doc.deleted = True
    doc.save()
    return redirect_to_next_url(request)

# notifications
def notification_list(request):
    return render(request, 'notifications/list.html', {
        'notifications': BaseNotificationForm.objects.all(),
    })

def view_notification(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    template_names = ['notifications/view/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    return render(request, template_names, {
        'documents': notification.documents.filter(deleted=False).order_by('doctype__name', '-date'),
        'notification_form': notification,
    })

def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.order_by('name')
    })

def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)

    form = notification_type.form_cls(request.POST or None)
    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')

    if request.method == 'POST':
        if form.is_valid() and document_formset.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            notification.save()
            notification.submission_forms = form.cleaned_data['submission_forms']
            notification.investigators = form.cleaned_data['investigators']
            notification.documents = document_formset.save()
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))

    template_names = ['notifications/creation/%s.html' % name for name in (form.__class__.__name__, 'base')]
    return render(request, template_names, {
        'notification_type': notification_type,
        'form': form,
        'document_formset': document_formset,
    })

def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    template_names = ['notifications/htmldoc/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    tpl = loader.select_template(template_names)
    html = tpl.render(Context({
        'notification': notification,
        'investigators': notification.investigators.order_by('ethics_commission__name', 'name'),
        'url': request.build_absolute_uri(),
    }))
    pdf = htmldoc(html.encode('ISO-8859-1'), webpage=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=notification_%s.pdf' % notification_pk
    return response
    

# submissions

def create_submission_form(request):
    formsets = {}
    for formset_cls in (MeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet):
        name = formset_cls.__name__.replace('FormFormSet', '').lower()
        formsets["%s_formset" % name] = formset_cls(request.POST or None, prefix=name)
    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')
    form = SubmissionFormForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()) and document_formset.is_valid():
            submission_form = form.save(commit=False)
            from random import randint
            submission = Submission.objects.create(ec_number="EK-%s" % randint(10000, 100000))
            submission_form.submission = submission
            submission_form.save()
            for formset in formsets.itervalues():
                for instance in formset.save(commit=False):
                    instance.submission_form = submission_form
                    instance.save()
            submission_form.documents = document_formset.save()
            return HttpResponseRedirect(reverse('ecs.core.views.view_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_formset': document_formset,
    }
    context.update(formsets)
    return render(request, 'submissions/form.html', context)

def view_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    return render(request, 'submissions/view.html', {
        'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
        'submission_form': submission_form,
        'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
    })

def submission_form_list(request):
    return render(request, 'submissions/list.html', {
        'submission_forms': SubmissionForm.objects.all().order_by('project_title')
    })