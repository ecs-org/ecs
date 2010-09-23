# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.forms.formsets import BaseFormSet, formset_factory
from django.utils.safestring import mark_safe


from ecs.documents.models import Document
from ecs.core.models import Investigator, InvestigatorEmployee, SubmissionForm, Measure, ForeignParticipatingCenter, NonTestedUsedDrug, Submission
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification
from ecs.core.models import MedicalCategory

from ecs.core.forms.fields import DateField, NullBooleanField, InvestigatorChoiceField, InvestigatorMultipleChoiceField
from ecs.core.forms.utils import ReadonlyFormMixin, ReadonlyFormSetMixin

def _unpickle(f, args, kwargs):
    return globals()[f.replace('FormFormSet', 'FormSet')](*args, **kwargs)
    
class ModelFormPickleMixin(object):
    def __reduce__(self):
        return (_unpickle, (self.__class__.__name__, (), {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}))
        
class ModelFormSetPickleMixin(object):
    def __reduce__(self):
        return (_unpickle, (self.__class__.__name__, (), {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}))

## notifications ##

class NotificationForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = Notification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')
        

class ProgressReportNotificationForm(NotificationForm):
    runs_till = DateField(required=True)

    class Meta:
        model = ProgressReportNotification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')

class CompletionReportNotificationForm(NotificationForm):
    completion_date = DateField(required=True)

    class Meta:
        model = CompletionReportNotification
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt')

## submissions ##

class SubmissionEditorForm(forms.ModelForm):
    class Meta:
        model = Submission

class SubmissionFormForm(ReadonlyFormMixin, ModelFormPickleMixin, forms.ModelForm):

    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)
    
    # non model fields (required for validation)
    invoice_differs_from_sponsor = forms.BooleanField(required=False, label=u'Der Rechnungsempfänger ist nicht der Sponsor')

    class Meta:
        model = SubmissionForm
        fields = (
            'project_title', 'german_project_title', 'eudract_number', 'specialism', 'clinical_phase', 'already_voted', 
            'project_type_non_reg_drug', 'project_type_reg_drug', 'project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication', 
            'project_type_medical_method', 'project_type_medical_device', 'project_type_medical_device_with_ce', 'project_type_medical_device_without_ce', 
            'project_type_medical_device_performance_evaluation', 'project_type_basic_research', 'project_type_genetic_study', 'project_type_register', 
            'project_type_biobank', 'project_type_retrospective', 'project_type_questionnaire', 'project_type_psychological_study', 'project_type_education_context', 
            'project_type_misc', 'subject_count', 'subject_minage', 'subject_maxage', 'subject_noncompetents', 'subject_males', 'subject_females', 'subject_childbearing', 
            'subject_duration', 'subject_duration_active', 'subject_duration_controls', 'subject_planned_total_duration', 'submitter_contact_gender', 
            'submitter_contact_first_name', 'submitter_contact_last_name', 'submitter_organisation', 'submitter_jobtitle', 'submitter_is_coordinator', 
            'submitter_is_main_investigator', 'submitter_is_sponsor', 'submitter_is_authorized_by_sponsor', 'submitter_agrees_to_publishing', 'sponsor_name', 
            'sponsor_contact_gender', 'sponsor_contact_first_name', 'sponsor_contact_last_name', 'sponsor_address1', 'sponsor_address2', 'sponsor_zip_code', 
            'sponsor_city', 'sponsor_phone', 'sponsor_fax', 'sponsor_email', 'invoice_differs_from_sponsor', 'invoice_name', 'invoice_contact_gender', 
            'invoice_contact_first_name', 'invoice_contact_last_name', 'invoice_address1', 'invoice_address2', 'invoice_zip_code', 'invoice_city', 'invoice_phone', 
            'invoice_fax', 'invoice_email', 'invoice_uid_verified_level1', 'invoice_uid_verified_level2', 'pharma_checked_substance', 'pharma_reference_substance', 
            'substance_registered_in_countries', 'substance_preexisting_clinical_tries', 'substance_p_c_t_countries', 'substance_p_c_t_phase', 'substance_p_c_t_period', 
            'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report', 'medtech_checked_product', 'medtech_reference_substance', 
            'medtech_product_name', 'medtech_manufacturer', 'medtech_certified_for_exact_indications', 'medtech_certified_for_other_indications', 'medtech_ce_symbol', 
            'medtech_manual_included', 'medtech_technical_safety_regulations', 'medtech_departure_from_regulations', 'insurance_name', 'insurance_address_1', 
            'insurance_phone', 'insurance_contract_number', 'insurance_validity', 'additional_therapy_info', 'german_summary', 'german_preclinical_results', 
            'german_primary_hypothesis', 'german_inclusion_exclusion_crit', 'german_ethical_info', 'german_protected_subjects_info', 'german_recruitment_info', 
            'german_consent_info', 'german_risks_info', 'german_benefits_info', 'german_relationship_info', 'german_concurrent_study_info', 'german_sideeffects_info', 
            'german_statistical_info', 'german_dataprotection_info', 'german_aftercare_info', 'german_payment_info', 'german_abort_info', 'german_dataaccess_info', 
            'german_financing_info', 'german_additional_info', 'study_plan_blind', 'study_plan_observer_blinded', 'study_plan_randomized', 'study_plan_parallelgroups', 
            'study_plan_controlled', 'study_plan_cross_over', 'study_plan_placebo', 'study_plan_factorized', 'study_plan_pilot_project', 'study_plan_equivalence_testing', 
            'study_plan_misc', 'study_plan_number_of_groups', 'study_plan_stratification', 'study_plan_sample_frequency', 'study_plan_primary_objectives', 
            'study_plan_null_hypothesis', 'study_plan_alternative_hypothesis', 'study_plan_secondary_objectives', 'study_plan_alpha', 'study_plan_power', 
            'study_plan_statalgorithm', 'study_plan_multiple_test_correction_algorithm', 'study_plan_dropout_ratio', 'study_plan_population_intention_to_treat', 
            'study_plan_population_per_protocol', 'study_plan_abort_crit', 'study_plan_planned_statalgorithm', 'study_plan_dataquality_checking', 'study_plan_datamanagement', 
            'study_plan_biometric_planning', 'study_plan_statistics_implementation', 'study_plan_dataprotection_reason', 'study_plan_dataprotection_dvr', 
            'study_plan_dataprotection_anonalgoritm', 'submitter_email',
        )
        
    def clean(self):
        cleaned_data = super(SubmissionFormForm, self).clean()
        return cleaned_data

## documents ##
        
class DocumentForm(ModelFormPickleMixin, forms.ModelForm):
    date = DateField(required=True)
    
    def clean(self):
        file = self.cleaned_data.get('file')
        if not self.cleaned_data.get('original_file_name') and file:
            self.cleaned_data['original_file_name'] = file.name
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(DocumentForm, self).save(commit=False)
        obj.original_file_name = self.cleaned_data.get('original_file_name')
        if commit:
            obj.save()
        return obj
    
    class Meta:
        model = Document
        exclude = ('uuid_document', 'hash', 'mimetype', 'pages', 'deleted', 'original_file_name', 'content_type', 'object_id')

class BaseDocumentFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Document.objects.none())
        super(BaseDocumentFormSet, self).__init__(*args, **kwargs)
        
DocumentFormSet = modelformset_factory(Document, formset=BaseDocumentFormSet, extra=1, form=DocumentForm)

## ##

class BaseForeignParticipatingCenterFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', ForeignParticipatingCenter.objects.none())
        super(BaseForeignParticipatingCenterFormSet, self).__init__(*args, **kwargs)

ForeignParticipatingCenterFormSet = modelformset_factory(ForeignParticipatingCenter, formset=BaseForeignParticipatingCenterFormSet, extra=1, exclude=('submission_form',))

class BaseNonTestedUsedDrugFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', NonTestedUsedDrug.objects.none())
        super(BaseNonTestedUsedDrugFormSet, self).__init__(*args, **kwargs)
        
NonTestedUsedDrugFormSet = modelformset_factory(NonTestedUsedDrug, formset=BaseNonTestedUsedDrugFormSet, extra=1, exclude=('submission_form',))

class MeasureForm(ModelFormPickleMixin, forms.ModelForm):
    category = forms.CharField(widget=forms.HiddenInput(attrs={'value': '6.1'}))
    
    class Meta:
        model = Measure
        exclude = ('submission_form',)
        
class RoutineMeasureForm(MeasureForm):
    category = forms.CharField(widget=forms.HiddenInput(attrs={'value': '6.2'}))

class BaseMeasureFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms if form.is_valid()]
        
MeasureFormSet = formset_factory(MeasureForm, formset=BaseMeasureFormSet, extra=1)
RoutineMeasureFormSet = formset_factory(RoutineMeasureForm, formset=BaseMeasureFormSet, extra=1)

class InvestigatorForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = Investigator
        fields = ('organisation', 'subject_count', 'ethics_commission', 'main', 
            'contact_gender', 'contact_first_name', 'contact_last_name',
            'phone', 'mobile', 'fax', 'email', 'jus_practicandi', 'specialist', 'certified',)

class BaseInvestigatorFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms[:self.total_form_count()] if form.is_valid() and form.has_changed()]

InvestigatorFormSet = formset_factory(InvestigatorForm, formset=BaseInvestigatorFormSet, extra=1) 

class InvestigatorEmployeeForm(ModelFormPickleMixin, forms.ModelForm):
    investigator_index = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

    class Meta:
        model = InvestigatorEmployee
        exclude = ('investigator',)

class BaseInvestigatorEmployeeFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms[:self.total_form_count()] if form.is_valid() and form.has_changed()]

InvestigatorEmployeeFormSet = formset_factory(InvestigatorEmployeeForm, formset=BaseInvestigatorEmployeeFormSet, extra=1)

