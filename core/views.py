# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader, Template
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.forms.models import inlineformset_factory

import settings

from ecs.core.models import Document, BaseNotificationForm, NotificationType, Submission, SubmissionForm
from ecs.core.forms import DocumentUploadForm, SubmissionFormForm
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

def file_uuid(doc_file):
    """returns md5 digest of a given file as uuid"""
    import hashlib
    s = doc_file.read()  # TODO optimize for large files! check if correct for binary files (e.g. random bytes)
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

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
    if request.method == 'POST':
        form = notification_type.form_cls(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            notification.save()
            notification.submission_forms = form.cleaned_data['submission_forms']
            notification.investigators = form.cleaned_data['investigators']
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))
    else:
        form = notification_type.form_cls()

    template_names = ['notifications/creation/%s.html' % name for name in (form.__class__.__name__, 'base')]
    return render(request, template_names, {
        'notification_type': notification_type,
        'form': form,
    })


def upload_document_for_notification(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    documents = notification.documents.filter(deleted=False).order_by('doctype__name', '-date')
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            # FIXME: this should be handled by the file storage system on the fly.
            document.uuid_document = file_uuid(document.file)
            document.uuid_document_revision = document.uuid_document
            document.file.seek(0)
            document.save()
            notification.documents.add(document)
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))
    else:
        form = DocumentUploadForm()

    return render(request, 'notifications/upload_document.html', {
        'notification': notification,
        'documents': documents,
        'form': form,
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

SUBMISSION_FORM_TABS = (
    (u'Eckdaten', [
        (u'Titel', ['project_title', 'german_project_title', 'eudract_number', 'specialism', 'clinical_phase', 'already_voted',]),
        (u'Art des Projekts', ['project_type_2_1_%s' % i for i in range(1, 10)]),
        (u'Zentren im Ausland', []),
        (u'Arzneimittelstudie', ['pharma_checked_substance', 'pharma_reference_substance']),
        (u'Medizinproduktestudie', ['medtech_checked_product', 'medtech_reference_substance']),
        (u'Prüfungsteilnehmer', [
            'subject_count', 'subject_minage', 'subject_maxage', 'subject_noncompetents', 'subject_males', 'subject_females', 
            'subject_childbearing', 'subject_duration', 'subject_duration_active', 'subject_duration_controls', 'subject_planned_total_duration',
        ]),
    ]),
    (u'Sponsor', [
        (u'Sponsor', [
            'sponsor_name', 'sponsor_contactname', 'sponsor_address1', 'sponsor_address2', 'sponsor_zip_code', 
            'sponsor_city', 'sponsor_phone', 'sponsor_fax', 'sponsor_email',
        ]),
        (u'Rechnungsempfänger', [
            'invoice_name', 'invoice_contactname', 'invoice_address1', 'invoice_address2', 'invoice_zip_code', 
            'invoice_city', 'invoice_phone', 'invoice_fax', 'invoice_email',
            'invoice_uid_verified_level1', 'invoice_uid_verified_level2',
        ]),
    ]),
    (u'AMG', [
        (None, [
            'substance_registered_in_countries', 'substance_preexisting_clinical_tries', 
            'substance_p_c_t_countries', 'substance_p_c_t_phase', 'substance_p_c_t_period', 
            'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report',
        ]),
    ]),
    (u'MPG', [
        (None, [
            'medtech_product_name', 'medtech_manufacturer', 'medtech_certified_for_exact_indications', 'medtech_certified_for_other_indications', 
            'medtech_ce_symbol', 'medtech_manual_included', 'medtech_technical_safety_regulations', 'medtech_departure_from_regulations',
        ]),
    ]),
    (u'Versicherung', [
        (None, [
            'insurance_name', 'insurance_address_1', 'insurance_phone', 'insurance_contract_number', 'insurance_validity',
        ]),
    ]),
    (u'Massnahmen', [
        (None, ['additional_therapy_info',]),
    ]),
    (u'Kurzfassung', [
        (None, [
            'german_summary', 'german_preclinical_results', 'german_primary_hypothesis', 'german_inclusion_exclusion_crit', 
            'german_ethical_info', 'german_protected_subjects_info', 'german_recruitment_info', 'german_consent_info', 'german_risks_info', 
            'german_benefits_info', 'german_relationship_info', 'german_concurrent_study_info', 'german_sideeffects_info', 
            'german_statistical_info', 'german_dataprotection_info', 'german_aftercare_info', 'german_payment_info', 'german_abort_info', 'german_dataaccess_info',
            'german_financing_info', 'german_additional_info',
        ]),
    ]),
    (u'Biometrie', [
        (None, [
            'study_plan_alpha', 'study_plan_power', 'study_plan_statalgorithm', 'study_plan_multiple_test_correction_algorithm', 'study_plan_dropout_ratio',
            'study_plan_8_3_1', 'study_plan_8_3_2', 'study_plan_abort_crit', 'study_plan_planned_statalgorithm', 'study_plan_dataquality_checking', 
            'study_plan_datamanagement', 'study_plan_biometric_planning', 'study_plan_statistics_implementation', 'study_plan_dataprotection_reason',
            'study_plan_dataprotection_dvr', 'study_plan_dataprotection_anonalgoritm', 
        ] + ['study_plan_8_1_%s' % i for i in range(1, 23) if i not in (4, 8)]),
    ]),
    (u'Unterlagen', []),
    (u'Antragsteller', [
        (None, [
            'submitter_name', 'submitter_organisation', 'submitter_jobtitle', 'submitter_is_coordinator', 'submitter_is_main_investigator', 'submitter_is_sponsor',
            'submitter_is_authorized_by_sponsor', 'submitter_sign_date', 'submitter_agrees_to_publishing',
        ]),
    ]),
    (u'Prüfer', []),
)

def create_submission_form(request):
    if request.method == 'POST':
        form = SubmissionFormForm(request.POST)
        if form.is_valid():
            submission_form = form.save(commit=False)
            from random import randint
            submission = Submission.objects.create(ec_number="EK-%s" % randint(10000, 100000))
            submission_form.submission = submission
            submission_form.save()
            return HttpResponseRedirect(reverse('ecs.core.views.view_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
        else:
            print form.errors
    else:
        form = SubmissionFormForm()
    return render(request, 'submissions/form.html', {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
    })

def view_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    return render(request, 'submissions/view.html', {
        'paper_form_fields': paper_forms.SUBMISSION_FIELD_DATA,
        'submission_form': submission_form,
    })
