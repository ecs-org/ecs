# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.forms.models import BaseModelFormSet, inlineformset_factory, modelformset_factory
from django.forms.formsets import BaseFormSet, formset_factory
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import F

from ecs.core.models import Investigator, InvestigatorEmployee, SubmissionForm, Measure, ForeignParticipatingCenter, NonTestedUsedDrug, Submission
from ecs.notifications.models import Notification, CompletionReportNotification, ProgressReportNotification, AmendmentNotification
from ecs.core.models import MedicalCategory

from ecs.core.forms.fields import DateField, NullBooleanField, MultiselectWidget, StrippedTextInput
from ecs.core.forms.utils import ReadonlyFormMixin, ReadonlyFormSetMixin
from ecs.utils.formutils import require_fields
from ecs.users.utils import get_current_user
from ecs.core.models.voting import FINAL_VOTE_RESULTS

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
        exclude = ('type', 'documents', 'investigators', 'date_of_receipt', 'user', 'timestamp')

class MultiNotificationForm(NotificationForm):
    def __init__(self, *args, **kwargs):
        super(MultiNotificationForm, self).__init__(*args, **kwargs)
        self.fields['submission_forms'].queryset = SubmissionForm.objects.filter(submission__current_submission_form__id=F('id'), presenter=get_current_user(), votes__result__in=FINAL_VOTE_RESULTS).order_by('submission__ec_number')

class SingleStudyNotificationForm(NotificationForm):
    submission_form = forms.ModelChoiceField(queryset=SubmissionForm.objects.all())
    
    def __init__(self, *args, **kwargs):
        super(SingleStudyNotificationForm, self).__init__(*args, **kwargs)
        self.fields['submission_form'].queryset = SubmissionForm.objects.filter(submission__current_submission_form__id=F('id'), presenter=get_current_user(), votes__result__in=FINAL_VOTE_RESULTS).order_by('submission__ec_number')

    class Meta:
        model = Notification
        exclude = NotificationForm._meta.exclude + ('submission_forms',)
        
    def get_submission_form(self):
        return self.cleaned_data['submission_form']
    
    def save(self, commit=True):
        obj = super(SingleStudyNotificationForm, self).save(commit=commit)
        if commit:
            obj.submission_forms = [self.get_submission_form()]
        else:
            old_save_m2m = self.save_m2m
            def _save_m2m():
                old_save_m2m()
                obj.submission_forms = [self.get_submission_form()]
            self.save_m2m = _save_m2m
        return obj

class ProgressReportNotificationForm(SingleStudyNotificationForm):
    runs_till = DateField(required=True)

    class Meta:
        model = ProgressReportNotification
        exclude = SingleStudyNotificationForm._meta.exclude

class CompletionReportNotificationForm(SingleStudyNotificationForm):
    completion_date = DateField(required=True)

    class Meta:
        model = CompletionReportNotification
        exclude = SingleStudyNotificationForm._meta.exclude

class AmendmentNotificationForm(NotificationForm):
    class Meta:
        model = AmendmentNotification
        exclude = NotificationForm._meta.exclude + ('submission_forms', 'old_submission_form', 'new_submission_form', 'diff')

## submissions ##

class SubmissionEditorForm(forms.ModelForm):
    class Meta:
        model = Submission


AMG_REQUIRED_FIELDS = (
    'substance_preexisting_clinical_tries', 'substance_p_c_t_phase', 'substance_p_c_t_period', 
    'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report', 'submission_type', 'eudract_number', 
    'pharma_checked_substance', 'pharma_reference_substance', 
)
AMG_FIELDS = AMG_REQUIRED_FIELDS + ('substance_registered_in_countries', 'substance_p_c_t_countries',)

MPG_FIELDS = (
    'medtech_checked_product', 'medtech_reference_substance', 
    'medtech_product_name', 'medtech_manufacturer', 'medtech_certified_for_exact_indications', 'medtech_certified_for_other_indications', 'medtech_ce_symbol', 
    'medtech_manual_included', 'medtech_technical_safety_regulations', 'medtech_departure_from_regulations', 
)

INSURANCE_FIELDS = (
    'insurance_name', 'insurance_address', 'insurance_phone', 'insurance_contract_number', 'insurance_validity'
)

INVOICE_REQUIRED_FIELDS = (
    'invoice_name', 'invoice_address', 'invoice_zip_code', 'invoice_city', 'invoice_phone', 'invoice_email'
)

class SubmissionFormForm(ReadonlyFormMixin, ModelFormPickleMixin, forms.ModelForm):

    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)
    
    # non model fields (required for validation)
    invoice_differs_from_sponsor = forms.BooleanField(required=False, label=_(u'The account beneficiary is not the sponsor'))

    class Meta:
        model = SubmissionForm
        fields = (
            'project_title', 'german_project_title', 'specialism', 'clinical_phase', 'already_voted', 'external_reviewer_suggestions',
            
            'project_type_non_reg_drug', 'project_type_reg_drug', 'project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication', 
            'project_type_medical_method', 'project_type_medical_device', 'project_type_medical_device_with_ce', 'project_type_medical_device_without_ce', 
            'project_type_medical_device_performance_evaluation', 'project_type_basic_research', 'project_type_genetic_study', 'project_type_register', 
            'project_type_biobank', 'project_type_retrospective', 'project_type_questionnaire', 'project_type_psychological_study', 'project_type_education_context', 
            'project_type_misc', 'project_type_nursing_study',
            
            'subject_count', 'subject_minage', 'subject_maxage', 'subject_noncompetents', 'subject_males', 'subject_females', 'subject_childbearing', 
            'subject_duration', 'subject_duration_active', 'subject_duration_controls', 'subject_planned_total_duration', 
            
            'submitter_contact_gender', 'submitter_contact_title', 'submitter_contact_first_name', 'submitter_contact_last_name', 
            'submitter_organisation', 'submitter_jobtitle', 'submitter_is_coordinator', 
            'submitter_is_main_investigator', 'submitter_is_sponsor', 'submitter_is_authorized_by_sponsor', 'sponsor_agrees_to_publishing', 'sponsor_name', 
            
            'sponsor_contact_gender', 'sponsor_contact_title', 'sponsor_contact_first_name', 'sponsor_contact_last_name', 
            'sponsor_address', 'sponsor_zip_code', 
            'sponsor_city', 'sponsor_phone', 'sponsor_fax', 'sponsor_email', 'sponsor_uid_verified_level1', 'sponsor_uid_verified_level2',
            'invoice_differs_from_sponsor',
            
            'invoice_name', 'invoice_contact_gender', 'invoice_contact_title', 'invoice_contact_first_name', 'invoice_contact_last_name', 
            'invoice_address', 'invoice_zip_code', 'invoice_city', 'invoice_phone', 'invoice_fax', 'invoice_email', 
            'invoice_uid_verified_level1', 'invoice_uid_verified_level2', 
            
            'additional_therapy_info', 
            'german_summary', 'german_preclinical_results', 'german_primary_hypothesis', 'german_inclusion_exclusion_crit', 'german_ethical_info', 
            'german_protected_subjects_info', 'german_recruitment_info', 'german_consent_info', 'german_risks_info', 'german_benefits_info', 'german_relationship_info', 
            'german_concurrent_study_info', 'german_sideeffects_info', 'german_statistical_info', 'german_dataprotection_info', 'german_aftercare_info', 'german_payment_info', 
            'german_abort_info', 'german_dataaccess_info', 'german_financing_info', 'german_additional_info', 
            
            'study_plan_blind', 'study_plan_observer_blinded', 'study_plan_randomized', 'study_plan_parallelgroups', 
            'study_plan_controlled', 'study_plan_cross_over', 'study_plan_placebo', 'study_plan_factorized', 'study_plan_pilot_project', 'study_plan_equivalence_testing', 
            'study_plan_misc', 'study_plan_number_of_groups', 'study_plan_stratification', 'study_plan_sample_frequency', 'study_plan_primary_objectives', 
            'study_plan_null_hypothesis', 'study_plan_alternative_hypothesis', 'study_plan_secondary_objectives', 'study_plan_alpha', 'study_plan_power', 
            'study_plan_statalgorithm', 'study_plan_multiple_test', 'study_plan_multiple_test_correction_algorithm', 'study_plan_dropout_ratio',
            'study_plan_population_intention_to_treat', 'study_plan_population_per_protocol', 'study_plan_interim_evaluation', 'study_plan_abort_crit',
            'study_plan_planned_statalgorithm', 'study_plan_dataquality_checking', 'study_plan_datamanagement', 
            'study_plan_biometric_planning', 'study_plan_statistics_implementation', 'study_plan_dataprotection_choice', 'study_plan_dataprotection_reason',
            'study_plan_dataprotection_dvr', 'study_plan_dataprotection_anonalgoritm', 'submitter_email', 'protocol_number',
        ) + AMG_FIELDS + MPG_FIELDS + INSURANCE_FIELDS

        widgets = {
            'sponsor_email': StrippedTextInput(),
            'invoice_email': StrippedTextInput(),
            'submitter_email': StrippedTextInput(),
        }

    def __init__(self, *args, **kwargs):
        rval = super(SubmissionFormForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'USE_TEXTBOXLIST', False):
            self.fields['substance_registered_in_countries'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'countries'})
            )
            self.fields['substance_p_c_t_countries'].widget = MultiselectWidget(
                url=lambda: reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'countries'})
            )
        return rval
    
    def clean(self):
        cleaned_data = super(SubmissionFormForm, self).clean()
        cleaned_data['project_type_reg_drug'] = any(self.cleaned_data.get(f, False) for f in ('project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication'))
        cleaned_data['project_type_medical_device'] = any(self.cleaned_data.get(f, False) for f in ('project_type_medical_device_with_ce', 'project_type_medical_device_without_ce', 'project_type_medical_device_performance_evaluation'))
        
        if any(cleaned_data.get(f, False) for f in ('project_type_reg_drug', 'project_type_non_reg_drug')):
            require_fields(self, AMG_REQUIRED_FIELDS)

        if cleaned_data.get('project_type_medical_device', False):
            require_fields(self, MPG_FIELDS)
            
        if any(cleaned_data.get(f, False) for f in ('project_type_medical_device_without_ce', 'project_type_reg_drug', 'project_type_non_reg_drug')):
            require_fields(self, INSURANCE_FIELDS)

        if cleaned_data.get('invoice_differs_from_sponsor', False):
            require_fields(self, INVOICE_REQUIRED_FIELDS)

        if cleaned_data.get('study_plan_interim_evaluation', False):
            require_fields(self, ('study_plan_abort_crit',))
        
        if cleaned_data.get('study_plan_multiple_test', False):
            require_fields(self, ('study_plan_multiple_test_correction_algorithm',))

        if cleaned_data.get('study_plan_dataprotection_choice', 'non-personal') == 'personal':
            require_fields(self, ('study_plan_dataprotection_reason', 'study_plan_dataprotection_dvr',))
        else:
            require_fields(self, ('study_plan_dataprotection_anonalgoritm',))

        return cleaned_data

## ##

class ForeignParticipatingCenterForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = ForeignParticipatingCenter
        exclude = ('submission_form',)

class BaseForeignParticipatingCenterFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms if form.is_valid()]

ForeignParticipatingCenterFormSet = formset_factory(ForeignParticipatingCenterForm, formset=BaseForeignParticipatingCenterFormSet, extra=0)

class NonTestedUsedDrugForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = NonTestedUsedDrug
        exclude = ('submission_form',)

class BaseNonTestedUsedDrugFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms if form.is_valid()]
        
NonTestedUsedDrugFormSet = formset_factory(NonTestedUsedDrugForm, formset=BaseNonTestedUsedDrugFormSet, extra=0)

class MeasureForm(ModelFormPickleMixin, forms.ModelForm):
    category = forms.CharField(widget=forms.HiddenInput(attrs={'value': '6.1'}))
    
    class Meta:
        model = Measure
        exclude = ('submission_form',)
        widgets = {
            'type': forms.Textarea(),
            'count': forms.Textarea(),
            'period': forms.Textarea(),
            'total': forms.Textarea(),
        }
        
class RoutineMeasureForm(MeasureForm):
    category = forms.CharField(widget=forms.HiddenInput(attrs={'value': '6.2'}))

class BaseMeasureFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms if form.is_valid()]
        
MeasureFormSet = formset_factory(MeasureForm, formset=BaseMeasureFormSet, extra=0)
RoutineMeasureFormSet = formset_factory(RoutineMeasureForm, formset=BaseMeasureFormSet, extra=0)

class InvestigatorForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = Investigator
        fields = ('organisation', 'subject_count', 'ethics_commission', 'main', 
            'contact_gender', 'contact_title', 'contact_first_name', 'contact_last_name',
            'phone', 'mobile', 'fax', 'email', 'jus_practicandi', 'specialist', 'certified',)
        widgets = {
            'email': StrippedTextInput(),
        }

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

_queries = {
    'new':              lambda s,u: s.new(),
    'next_meeting':     lambda s,u: s.next_meeting(),
    'other_meetings':   lambda s,u: s.exclude(pk__in=s.new().values('pk').query).exclude(pk__in=s.next_meeting().values('pk').query),
    'amg':              lambda s,u: s.amg(),
    'mpg':              lambda s,u: s.mpg(),
    'thesis':           lambda s,u: s.thesis(),
    'other':            lambda s,u: s.exclude(pk__in=s.amg().values('pk').query).exclude(pk__in=s.mpg().values('pk').query).exclude(pk__in=s.thesis().values('pk').query),
    'b2':               lambda s,u: s.b2(),
    'b3':               lambda s,u: s.b3(),
    'b4':               lambda s,u: s.b4(),
    'other_votes':      lambda s,u: s.exclude(pk__in=s.b2().values('pk').query).exclude(pk__in=s.b3().values('pk').query).exclude(pk__in=s.b4().values('pk').query),
    'mine':             lambda s,u: s.mine(u),
    'assigned':         lambda s,u: s.reviewed_by_user(u),
    'other_studies':    lambda s,u: s.exclude(pk__in=s.mine(u).values('pk').query).exclude(pk__in=s.reviewed_by_user(u).values('pk').query),
}

class SubmissionFilterForm(forms.Form):
    layout = ()
    page = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, data=None, *args, **kwargs):
        filter_defaults = dict(page='1')

        keys = set(self.__class__.base_fields.keys())
        keys.remove('page')

        for key in keys:
            filter_defaults[key] = 'on'

        data = data or filter_defaults
        return super(SubmissionFilterForm, self).__init__(data, *args, **kwargs)

    def filter_submissions(self, submissions, user):
        self.is_valid()   # force clean

        for row in self.layout:
            fnames = [x[0] for x in row]
            new = submissions.none()
            if all([self.cleaned_data[fname] for fname in fnames]):
                new = submissions.all()
            else:
                for fname in fnames:
                    if self.cleaned_data[fname]:
                        new |= _queries[fname](submissions, user)
            submissions = new

        return submissions

class SubmissionWidgetFilterForm(SubmissionFilterForm):
    layout = (
        (
            ('new', _('New')),
            ('next_meeting', _('Next Meeting')),
            ('other_meetings', _('Other Meetings'))
        ),
        (
            ('amg', _('AMG')),
            ('mpg', _('MPG')),
            ('thesis', _('Thesis')),
            ('other', _('Other')),
        ),
    )
    new = forms.BooleanField(required=False)
    next_meeting = forms.BooleanField(required=False)
    other_meetings = forms.BooleanField(required=False)
    amg = forms.BooleanField(required=False)
    mpg = forms.BooleanField(required=False)
    thesis = forms.BooleanField(required=False)
    other = forms.BooleanField(required=False)

class SubmissionListFilterForm(SubmissionWidgetFilterForm):
    layout = (
        (
            ('new', _('New')),
            ('next_meeting', _('Next Meeting')),
            ('other_meetings', _('Other Meetings'))
        ),
        (
            ('amg', _('AMG')),
            ('mpg', _('MPG')),
            ('thesis', _('Thesis')),
            ('other', _('Other')),
        ),
        (
            ('b2', _('B2 Votes')),
            ('b3', _('B3 Votes')),
            ('b4', _('B4 Votes')),
            ('other_votes', _('Other Votes')),
        ),
    )
    b2 = forms.BooleanField(required=False)
    b3 = forms.BooleanField(required=False)
    b4 = forms.BooleanField(required=False)
    other_votes = forms.BooleanField(required=False)

class SubmissionListFullFilterForm(SubmissionListFilterForm):
    layout = (
        (
            ('new', _('New')),
            ('next_meeting', _('Next Meeting')),
            ('other_meetings', _('Other Meetings'))
        ),
        (
            ('amg', _('AMG')),
            ('mpg', _('MPG')),
            ('thesis', _('Thesis')),
            ('other', _('Other')),
        ),
        (
            ('b2', _('B2 Votes')),
            ('b3', _('B3 Votes')),
            ('b4', _('B4 Votes')),
            ('other_votes', _('Other Votes')),
        ),
        (
            ('mine', _('Mine')),
            ('assigned', _('Assigned')),
            ('other_studies', _('Other Studies')),
        ),
    )
    mine = forms.BooleanField(required=False)
    assigned = forms.BooleanField(required=False)
    other_studies = forms.BooleanField(required=False)

class SubmissionImportForm(forms.Form):
    file = forms.FileField(label=_('file'))

    def clean_file(self):
        f = self.cleaned_data['file']
        from ecs.core.serializer import Serializer
        serializer = Serializer()
        try:
            self.submission_form = serializer.read(self.cleaned_data['file'])
        except Exception as e:
            import traceback
            traceback.print_exc(e)
            self._errors['file'] = self.error_class([_(u'This file is not a valid ECX archive.')])
        f.seek(0)
        return f

