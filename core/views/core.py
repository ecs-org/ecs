# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.forms.models import inlineformset_factory, model_to_dict
from django.conf import settings

from ecs.core.views.utils import render, redirect_to_next_url
from ecs.core.models import Document, Notification, NotificationType, Submission, SubmissionForm, Investigator, MedicalCategory
from ecs.core.forms import DocumentFormSet, SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet, InvestigatorFormSet, InvestigatorEmployeeFormSet
from ecs.core.forms.layout import SUBMISSION_FORM_TABS, NOTIFICATION_FORM_TABS
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

def get_submission_formsets(data=None, instance=None):
    formset_classes = [
        # (prefix, formset_class, callable SubmissionForm -> initial data)
        ('measure', MeasureFormSet, lambda sf: sf.measures.filter(category='6.1')),
        ('routinemeasure', RoutineMeasureFormSet, lambda sf: sf.measures.filter(category='6.2')),
        ('nontesteduseddrug', NonTestedUsedDrugFormSet, lambda sf: sf.nontesteduseddrug_set.all()),
        ('foreignparticipatingcenter', ForeignParticipatingCenterFormSet, lambda sf: sf.foreignparticipatingcenter_set.all()),
        ('investigator', InvestigatorFormSet, lambda sf: sf.investigators.all()),
    ]
    formsets = {}
    for name, formset_cls, initial in formset_classes:
        kwargs = {'prefix': name}
        if instance:
            kwargs['initial'] = [model_to_dict(obj, exclude=('id',)) for obj in initial(instance).order_by('id')]
        formsets[name] = formset_cls(data, **kwargs)
    
    employees = []
    if instance:
        for index, investigator in enumerate(formsets['investigator'].queryset):
            for employee in investigator.investigatoremployee_set.all():
                employee_dict = model_to_dict(employee, exclude=('id',))
                employee_dict['investigator_index'] = index
                employees.append(employee_dict)
    formsets['investigatoremployee'] = InvestigatorEmployeeFormSet(data, initial=employees or None, prefix='investigatoremployee')
    return formsets

def copy_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    
    docstash = DocStash.objects.create(group='ecs.core.views.core.create_submission_form', owner=request.user)
    with docstash.transaction():
        docstash.update({
            'form': SubmissionFormForm(data=None, initial=model_to_dict(submission_form)),
            'formsets': get_submission_formsets(instance=submission_form),
            'submission': submission_form.submission,
            'documents': list(submission_form.documents.all().order_by('pk')),
        })
        docstash.name = "%s" % submission_form.project_title
    return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': docstash.key}))


# submissions
@with_docstash_transaction
def create_submission_form(request):
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash['form']
        formsets = request.docstash['formsets']
    else:
        form = SubmissionFormForm(request.POST or None)
        formsets = get_submission_formsets(request.POST or None)

    document_formset = DocumentFormSet(request.POST or None, request.FILES or None, prefix='document')

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.update({
            'form': form,
            'formsets': formsets,
            'documents': list(Document.objects.filter(pk__in=map(int, request.POST.getlist('documents')))),
        })
        request.docstash.name = "%s" % request.POST.get('project_title', '')

        if autosave:
            return HttpResponse('autosave successfull')
        
        if document_formset.is_valid():
            request.docstash['documents'] = request.docstash['documents'] + document_formset.save()
            document_formset = DocumentFormSet(prefix='document')

        if submit and form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()):
            submission_form = form.save(commit=False)
            submission = request.docstash.get('submission') or Submission.objects.create()
            submission_form.submission = submission
            submission_form.save()
            submission_form.documents = request.docstash['documents']
            
            formsets = formsets.copy()
            investigators = formsets.pop('investigator').save(commit=False)
            for investigator in investigators:
                investigator.submission_form = submission_form
                investigator.save()
            for i, employee in enumerate(formsets.pop('investigatoremployee').save(commit=False)):
                employee.submission = investigators[int(request.POST['investigatoremployee-%s-investigator_index' % i])]  # TODO rename employee.submission to employee.investigator
                employee.save()

            for formset in formsets.itervalues():
                for instance in formset.save(commit=False):
                    instance.submission_form = submission_form
                    instance.save()
            return HttpResponseRedirect(reverse('ecs.core.views.view_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_formset': document_formset,
        'documents': request.docstash.get('documents', []),
    }
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
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
    
