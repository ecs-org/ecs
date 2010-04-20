# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.forms.models import inlineformset_factory
from django.conf import settings

from ecs.core.views.utils import render, redirect_to_next_url
from ecs.core.models import Document, Notification, NotificationType, Submission, SubmissionForm, Investigator
from ecs.core.forms import DocumentFormSet, SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet, InvestigatorFormSet, InvestigatorEmployeeFormSet
from ecs.core.forms.layout import SUBMISSION_FORM_TABS, NOTIFICATION_FORM_TABS
from ecs.utils.htmldoc import htmldoc
from ecs.utils.xhtml2pdf import xhtml2pdf
from ecs.core import paper_forms
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash

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
    investigators = Investigator.objects.filter(submission__in=submission_forms)
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
    data = request.POST or request.docstash.get_query_dict() or None

    form = notification_type.form_cls(data or None)
    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')
    
    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        autosave = request.POST.get('autosave', False)
        
        request.docstash.post(request.POST, exclude=lambda name: name.startswith('document-'))
        request.docstash['type_id'] = notification_type_pk
        request.docstash.name = "%s" % notification_type.name
        
        if autosave:
            return HttpResponse('autosave successful')
        
        if document_formset.is_valid():
            request.docstash['documents'] = request.docstash.get('documents', []) + [doc.pk for doc in document_formset.save()]
            document_formset = DocumentFormSet(prefix='document')
        
        
        if submit and form.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            notification.save()
            submission_forms = form.cleaned_data['submission_forms']
            notification.submission_forms = submission_forms
            notification.investigators.add(*Investigator.objects.filter(submission__in=submission_forms))
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))

    documents = Document.objects.filter(pk__in=request.docstash.get('documents', []))
    return render(request, 'notifications/form.html', {
        'notification_type': notification_type,
        'form': form,
        'tabs': NOTIFICATION_FORM_TABS[form.__class__],
        'document_formset': document_formset,
        'documents': documents,
    })

def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
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

def notification_xhtml2pdf(request, notification_pk=None):
    notification = get_object_or_404(Notification, pk=notification_pk)
    template_names = ['notifications/xhtml2pdf/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    print template_names
    tpl = loader.select_template(template_names)
    html = tpl.render(Context({
        'notification': notification,
        'investigators': notification.investigators.order_by('ethics_commission__name', 'name'),
        'url': request.build_absolute_uri(),
    }))
    pdf = xhtml2pdf(html)
    assert len(pdf) > 0
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=notification_%s.pdf' % notification_pk
    return response
    

# submissions
@with_docstash_transaction
def create_submission_form(request):
    data = request.POST or request.docstash.get_query_dict() or None
        
    formsets = {
        'measure': MeasureFormSet,
        'routinemeasure': RoutineMeasureFormSet,
        'nontesteduseddrug': NonTestedUsedDrugFormSet,
        'foreignparticipatingcenter': ForeignParticipatingCenterFormSet,
    }
    formsets = dict(('%s_formset' % name, formset_cls(data, prefix=name)) for name, formset_cls in formsets.iteritems())
    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')
    investigator_formset = InvestigatorFormSet(data, prefix='investigator')
    investigatoremployee_formset = InvestigatorEmployeeFormSet(data, prefix='investigatoremployee')
    form = SubmissionFormForm(data)

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.post(request.POST, exclude=lambda name: name.startswith('document-'))
        request.docstash.name = "%s" % request.POST.get('project_title', '')

        if autosave:
            return HttpResponse('autosave successfull')
        
        if document_formset.is_valid():
            request.docstash['documents'] = request.docstash.get('documents', []) + [doc.pk for doc in document_formset.save()]
            document_formset = DocumentFormSet(prefix='document')
        
        if submit and form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()) and investigator_formset.is_valid() and investigatoremployee_formset.is_valid():
            submission_form = form.save(commit=False)
            from random import randint
            submission = Submission.objects.create(ec_number="EK-%s" % randint(10000, 100000))
            submission_form.submission = submission
            submission_form.save()
            investigators = investigator_formset.save(commit=False)
            for investigator in investigators:
              investigator.submission = submission_form
              import datetime
              investigator.sign_date = datetime.date.today() # TODO remove after model refactoring
              investigator.save()
            for i, employee in enumerate(investigatoremployee_formset.save(commit=False)):
                employee.submission = investigators[int(request.POST['investigatoremployee-%s-investigator_index' % i])]  # TODO rename employee.submission to employee.investigator
                employee.save()
            for formset in formsets.itervalues():
                for instance in formset.save(commit=False):
                    instance.submission_form = submission_form
                    instance.save()
            submission_form.documents = Document.objects.filter(pk__in=request.docstash.get('documents', []))
            return HttpResponseRedirect(reverse('ecs.core.views.view_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    
    documents = Document.objects.filter(pk__in=request.docstash.get('documents', []))
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_formset': document_formset,
        'documents': documents,
        'investigator_formset': investigator_formset,
        'investigatoremployee_formset': investigatoremployee_formset,
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


def submission_pdf(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    html = render(request, 'submissions/xhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
            'submission_form': submission_form,
            'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
            }).content
    pdf = xhtml2pdf(html)
    assert len(pdf) > 0
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=submission_%s.pdf' % submission_form_pk
    return response


def submission_form_list(request):
    return render(request, 'submissions/list.html', {
        'submission_forms': SubmissionForm.objects.all().order_by('project_title'),
        'stashed_submission_forms': DocStash.objects.filter(group='ecs.core.views.core.create_submission_form'),
    })
    
