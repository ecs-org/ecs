import logging
from datetime import timedelta
from django import forms
from django.forms.formsets import BaseFormSet, formset_factory
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from django_countries import countries

from ecs.core.models import Investigator, InvestigatorEmployee, SubmissionForm, Measure, ForeignParticipatingCenter, \
    NonTestedUsedDrug, Submission, TemporaryAuthorization, AdvancedSettings, EthicsCommission

from ecs.utils.formutils import ModelFormPickleMixin, require_fields, TranslatedModelForm
from ecs.core.forms.fields import StrippedTextInput, NullBooleanField, MultiAutocompleteWidget, ReadonlyTextarea, ReadonlyTextInput, \
    EmailUserSelectWidget, AutocompleteWidget, DateTimeField
from ecs.core.forms.utils import ReadonlyFormMixin, ReadonlyFormSetMixin
from ecs.users.utils import get_current_user


def _unpickle(f, args, kwargs):
    return globals()[f.replace('FormFormSet', 'FormSet')](*args, **kwargs)

class ModelFormSetPickleMixin(object):
    def __reduce__(self):
        return (_unpickle, (self.__class__.__name__, (), {'data': self.data or None, 'prefix': self.prefix, 'initial': self.initial}))


## submissions ##

AMG_REQUIRED_FIELDS = (
    'substance_preexisting_clinical_tries', 'submission_type', 'eudract_number',
    'pharma_checked_substance', 'pharma_reference_substance',
)
AMG_FIELDS = AMG_REQUIRED_FIELDS + ('substance_registered_in_countries', 'substance_p_c_t_countries','substance_p_c_t_phase', 'substance_p_c_t_period',
    'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report',)

MPG_FIELDS = (
    'medtech_checked_product', 'medtech_reference_substance',
    'medtech_product_name', 'medtech_manufacturer', 'medtech_certified_for_exact_indications', 'medtech_certified_for_other_indications', 'medtech_ce_symbol',
    'medtech_manual_included', 'medtech_technical_safety_regulations', 'medtech_departure_from_regulations',
)

INSURANCE_FIELDS = (
    'insurance_not_required', 'insurance_name', 'insurance_address', 'insurance_phone', 'insurance_contract_number', 'insurance_validity'
)

INVOICE_REQUIRED_FIELDS = (
    'invoice_name', 'invoice_contact_gender', 'invoice_contact_first_name', 'invoice_contact_last_name', 'invoice_address',
    'invoice_zip_code', 'invoice_city', 'invoice_phone', 'invoice_email',
)

class SubmissionFormForm(ReadonlyFormMixin, ModelFormPickleMixin, forms.ModelForm):
    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)
    substance_registered_in_countries = forms.MultipleChoiceField(
        choices=countries, required=False,
        widget=MultiAutocompleteWidget('countries')
    )
    substance_p_c_t_countries = forms.MultipleChoiceField(
        choices=countries, required=False,
        widget=MultiAutocompleteWidget('countries')
    )

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)

    # non model fields (required for validation)
    invoice_differs_from_sponsor = forms.BooleanField(required=False, label=_('The account beneficiary is not the sponsor'))

    class Meta:
        model = SubmissionForm
        fields = (
            'project_title', 'german_project_title', 'specialism', 'clinical_phase', 'already_voted',

            'project_type_non_reg_drug', 'project_type_reg_drug', 'project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication',
            'project_type_medical_method', 'project_type_medical_device', 'project_type_medical_device_with_ce', 'project_type_medical_device_without_ce',
            'project_type_medical_device_performance_evaluation', 'project_type_basic_research', 'project_type_genetic_study', 'project_type_register',
            'project_type_biobank', 'project_type_retrospective', 'project_type_questionnaire', 'project_type_psychological_study', 'project_type_education_context',
            'project_type_non_interventional_study', 'project_type_gender_medicine', 'project_type_misc', 'project_type_nursing_study',

            'subject_count', 'subject_minage', 'subject_maxage', 'subject_noncompetents', 'subject_males', 'subject_females', 'subject_childbearing',
            'subject_duration', 'subject_duration_active', 'subject_duration_controls', 'subject_planned_total_duration',

            'submitter_contact_gender', 'submitter_contact_title', 'submitter_contact_first_name', 'submitter_contact_last_name',
            'submitter_organisation', 'submitter_jobtitle', 'submitter_is_coordinator',
            'submitter_is_main_investigator', 'submitter_is_sponsor', 'submitter_is_authorized_by_sponsor', 'sponsor_name',

            'sponsor_contact_gender', 'sponsor_contact_title', 'sponsor_contact_first_name', 'sponsor_contact_last_name',
            'sponsor_address', 'sponsor_zip_code',
            'sponsor_city', 'sponsor_phone', 'sponsor_fax', 'sponsor_email', 'sponsor_uid', 'invoice_differs_from_sponsor',

            'invoice_name', 'invoice_contact_gender', 'invoice_contact_title', 'invoice_contact_first_name', 'invoice_contact_last_name',
            'invoice_address', 'invoice_zip_code', 'invoice_city', 'invoice_phone', 'invoice_fax', 'invoice_email', 'invoice_uid',

            'additional_therapy_info',
            'german_summary', 'german_preclinical_results', 'german_primary_hypothesis', 'german_inclusion_exclusion_crit', 'german_ethical_info',
            'german_protected_subjects_info', 'german_recruitment_info', 'german_consent_info', 'german_risks_info', 'german_benefits_info', 'german_relationship_info',
            'german_concurrent_study_info', 'german_sideeffects_info', 'german_statistical_info', 'german_dataprotection_info', 'german_aftercare_info', 'german_payment_info',
            'german_abort_info', 'german_dataaccess_info', 'german_financing_info', 'german_additional_info',

            'study_plan_blind', 'study_plan_observer_blinded', 'study_plan_randomized', 'study_plan_parallelgroups',
            'study_plan_controlled', 'study_plan_cross_over', 'study_plan_placebo', 'study_plan_factorized', 'study_plan_pilot_project', 'study_plan_equivalence_testing',
            'study_plan_misc', 'study_plan_number_of_groups', 'study_plan_stratification', 'study_plan_sample_frequency', 'study_plan_primary_objectives',
            'study_plan_null_hypothesis', 'study_plan_alternative_hypothesis', 'study_plan_secondary_objectives', 'study_plan_alpha', 'study_plan_alpha_sided', 'study_plan_power',
            'study_plan_statalgorithm', 'study_plan_multiple_test', 'study_plan_multiple_test_correction_algorithm', 'study_plan_dropout_ratio',
            'study_plan_population_intention_to_treat', 'study_plan_population_per_protocol', 'study_plan_interim_evaluation', 'study_plan_abort_crit',
            'study_plan_planned_statalgorithm', 'study_plan_dataquality_checking', 'study_plan_datamanagement',
            'study_plan_biometric_planning', 'study_plan_statistics_implementation', 'study_plan_dataprotection_choice', 'study_plan_dataprotection_reason',
            'study_plan_dataprotection_dvr', 'study_plan_dataprotection_anonalgoritm', 'submitter_email',
        ) + AMG_FIELDS + MPG_FIELDS + INSURANCE_FIELDS

    def __init__(self, *args, **kwargs):
        rval = super(SubmissionFormForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.EmailField):
                field.widget = StrippedTextInput()
                if self.readonly:
                    field.widget.mark_readonly()
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

        if cleaned_data.get('substance_preexisting_clinical_tries') == True:
            require_fields(self, ('substance_p_c_t_phase', 'substance_p_c_t_period', 'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report',))

        return cleaned_data


## ##

class ForeignParticipatingCenterForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = ForeignParticipatingCenter
        exclude = ('submission_form',)
        widgets = {
            'name': ReadonlyTextInput(attrs={'size': 50}),
            'investigator_name': ReadonlyTextInput(attrs={'size': 40}),
        }

class BaseForeignParticipatingCenterFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms if form.is_valid()]

ForeignParticipatingCenterFormSet = formset_factory(ForeignParticipatingCenterForm, formset=BaseForeignParticipatingCenterFormSet, extra=0)

class NonTestedUsedDrugForm(ModelFormPickleMixin, forms.ModelForm):
    class Meta:
        model = NonTestedUsedDrug
        exclude = ('submission_form',)
        widgets = {
            'generic_name': ReadonlyTextInput(attrs={'cols': 30}),
            'preparation_form': ReadonlyTextInput(attrs={'cols': 30}),
            'dosage': ReadonlyTextInput(attrs={'cols': 30}),
        }

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
            'type': ReadonlyTextarea(attrs={'cols': 30}),
            'count': ReadonlyTextarea(attrs={'cols': 30}),
            'period': ReadonlyTextarea(attrs={'cols': 30}),
            'total': ReadonlyTextarea(attrs={'cols': 30}),
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

class PresenterChangeForm(forms.ModelForm):
    presenter = forms.ModelChoiceField(
        User.objects.filter(is_active=True), required=True,
        error_messages={'required': _('Please enter a valid e-mail address')},
        label=_('Presenter'),
        widget=EmailUserSelectWidget()
    )

    class Meta:
        model = Submission
        fields = ('presenter',)

    def __init__(self, *args, **kwargs):
        super(PresenterChangeForm, self).__init__(*args, **kwargs)
        if get_current_user().profile.is_internal:
            self.fields['presenter'].widget = \
                AutocompleteWidget('users')

class SusarPresenterChangeForm(forms.ModelForm):
    susar_presenter = forms.ModelChoiceField(
        User.objects.filter(is_active=True), required=True,
        error_messages={'required': _('Please enter a valid e-mail address')},
        label=_('Susar Presenter'),
        widget=EmailUserSelectWidget()
    )

    class Meta:
        model = Submission
        fields = ('susar_presenter',)

    def __init__(self, *args, **kwargs):
        super(SusarPresenterChangeForm, self).__init__(*args, **kwargs)
        if get_current_user().profile.is_internal:
            self.fields['susar_presenter'].widget = \
                AutocompleteWidget('users')

class BaseInvestigatorFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        return [form.save(commit=commit) for form in self.forms[:self.total_form_count()] if form.is_valid() and form.has_changed()]

    def clean(self):
        super(BaseInvestigatorFormSet, self).clean()
        changed_forms = [form for form in self.forms[:self.total_form_count()] if form.is_valid() and form.has_changed()]
        if len(changed_forms) < 1:
            raise forms.ValidationError(_('At least one centre is required.'))

        if any(self.errors):
            return
        elif not len([f for f in self.forms[:self.total_form_count()] if f.cleaned_data.get('main', False)]) == 1:
            raise forms.ValidationError(_('Please select exactly one primary investigator.'))

InvestigatorFormSet = formset_factory(InvestigatorForm, formset=BaseInvestigatorFormSet, extra=1)

class InvestigatorEmployeeForm(ModelFormPickleMixin, forms.ModelForm):
    investigator_index = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

    class Meta:
        model = InvestigatorEmployee
        exclude = ('investigator',)
        widgets = {
            'title': ReadonlyTextInput(attrs={'cols': 25}),
            'firstname': ReadonlyTextInput(attrs={'cols': 20}),
            'surname': ReadonlyTextInput(attrs={'cols': 20}),
            'organisation': ReadonlyTextInput(attrs={'cols': 50}),
        }

class BaseInvestigatorEmployeeFormSet(ReadonlyFormSetMixin, ModelFormSetPickleMixin, BaseFormSet):
    def save(self, commit=True):
        employees = []
        for form in self.forms[:self.total_form_count()]:
            if form.is_valid() and form.has_changed():
                employee = form.save(commit=commit)
                employee.investigator_index = form.cleaned_data['investigator_index']
                employees += [employee]
        return employees

InvestigatorEmployeeFormSet = formset_factory(InvestigatorEmployeeForm, formset=BaseInvestigatorEmployeeFormSet, extra=1)


_queries = {
    'past_meetings':    lambda s,u: s.past_meetings(),
    'next_meeting':     lambda s,u: s.next_meeting(),
    'upcoming_meetings':lambda s,u: s.upcoming_meetings().exclude(pk__in=s.next_meeting().values('pk').query),
    'no_meeting':       lambda s,u: s.no_meeting(),
    'new':              lambda s,u: s.new(),
    'other_meetings':   lambda s,u: s.exclude(pk__in=s.new().values('pk').query).exclude(pk__in=s.next_meeting().values('pk').query),

    'amg':              lambda s,u: s.amg(),
    'mpg':              lambda s,u: s.mpg(),
    'other':            lambda s,u: s.not_amg_and_not_mpg(),

    # lane filters
    'not_categorized':  lambda s,u: s.filter(workflow_lane=None),
    'board':            lambda s,u: s.for_board_lane(),
    'thesis':           lambda s,u: s.for_thesis_lane(),
    'expedited':        lambda s,u: s.expedited(),
    'local_ec':         lambda s,u: s.localec(),

    # vote filters
    'b2':               lambda s,u: s.b2(include_pending=u.profile.is_internal),
    'b3':               lambda s,u: s.b3(include_pending=u.profile.is_internal),
    'other_votes':      lambda s,u: s.b1(include_pending=u.profile.is_internal) |
        s.b4(include_pending=u.profile.is_internal) |
        s.b5(include_pending=u.profile.is_internal),
    'no_votes':         lambda s,u: s.without_vote(include_pending=u.profile.is_internal),

    'mine':             lambda s,u: s.mine(u),
    'assigned':         lambda s,u: s.reviewed_by_user(u),
    'other_studies':    lambda s,u: s.exclude(pk__in=s.mine(u).values('pk').query).exclude(pk__in=s.reviewed_by_user(u).values('pk').query),
}

_labels = {
    'past_meetings': _('Past Meetings'),
    'next_meeting': _('Next Meeting'),
    'upcoming_meetings': _('Upcoming Meetings'),
    'no_meeting': _('No Meeting'),

    'amg': _('AMG'),
    'mpg': _('MPG'),
    'other': _('Other'),

    'not_categorized': _('Not Categorized'),
    'board': _('board'),
    'thesis': _('Thesis'),
    'expedited': _('Expedited'),
    'local_ec': _('Local EC'),

    'b2': _('B2 Votes'),
    'b3': _('B3 Votes'),
    'other_votes': _('Other Votes'),
    'no_votes': _('No Votes'),

    'mine': _('Mine'),
    'assigned': _('Assigned'),
    'other_studies': _('Other Studies'),
}

class SubmissionFilterFormMetaclass(forms.forms.DeclarativeFieldsMetaclass):
    def __new__(cls, name, bases, attrs):
        newcls = super(SubmissionFilterFormMetaclass, cls).__new__(cls, name, bases, attrs)
        for row in attrs['layout']:
            for name in row:
                if not hasattr(newcls, name):
                    newcls.base_fields[name] = forms.BooleanField(required=False, label=_labels[name])
        return newcls

class SubmissionFilterForm(forms.Form, metaclass=SubmissionFilterFormMetaclass):
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
            new = submissions.none()
            if all(self.cleaned_data[f] for f in row):
                new = submissions.all()
            else:
                for f in row:
                    if self.cleaned_data[f]:
                        new |= _queries[f](submissions, user)
            submissions = new

        return submissions

FILTER_MEETINGS = ('past_meetings', 'next_meeting', 'upcoming_meetings', 'no_meeting')
FILTER_TYPE = ('amg', 'mpg', 'other')
FILTER_LANE = ('board', 'thesis', 'expedited', 'local_ec', 'not_categorized')
FILTER_VOTES = ('b2', 'b3', 'other_votes', 'no_votes')
FILTER_ASSIGNMENT = ('mine', 'assigned', 'other_studies')

class SubmissionMinimalFilterForm(SubmissionFilterForm):
    layout = ()

class SubmissionWidgetFilterForm(SubmissionFilterForm):
    layout = (FILTER_MEETINGS, FILTER_LANE, FILTER_TYPE)

class AssignedSubmissionsFilterForm(SubmissionFilterForm):
    layout = (FILTER_MEETINGS, FILTER_LANE, FILTER_TYPE, FILTER_VOTES)

class MySubmissionsFilterForm(SubmissionFilterForm):
    layout = (FILTER_VOTES,)

class AllSubmissionsFilterForm(SubmissionFilterForm):
    layout = (FILTER_MEETINGS, FILTER_LANE, FILTER_TYPE, FILTER_VOTES, FILTER_ASSIGNMENT)


import_error_logger = logging.getLogger('ecx-import')

class SubmissionImportForm(forms.Form):
    file = forms.FileField(label=_('file'))

    def clean_file(self):
        f = self.cleaned_data['file']
        from ecs.core.serializer import Serializer
        serializer = Serializer()
        try:
            with transaction.atomic():
                self.submission_form = serializer.read(self.cleaned_data['file'])
        except Exception as e:
            import_error_logger.debug('invalid ecx file')
            self.add_error('file', _('This file is not a valid ECX archive.'))
        f.seek(0)
        return f

class TemporaryAuthorizationForm(TranslatedModelForm):
    start = DateTimeField(initial=timezone.now)
    end = DateTimeField(initial=lambda: timezone.now() + timedelta(days=30))

    def __init__(self, *args, **kwargs):
        super(TemporaryAuthorizationForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = \
            self.fields['user'].queryset.select_related('profile')

    class Meta:
        model = TemporaryAuthorization
        exclude = ('submission',)
        widgets = {
            'user': AutocompleteWidget('users'),
        }
        labels = {
            'user': _('User'),
            'start': _('Start'),
            'end': _('End'),
        }

class AdvancedSettingsForm(TranslatedModelForm):
    class Meta:
        model = AdvancedSettings
        fields = ('default_contact',)
        widgets = {
            'default_contact': AutocompleteWidget('internal-users'),
        }
        labels = {
            'default_contact': _('Default Contact'),
        }

EthicsCommissionFormSet = modelformset_factory(EthicsCommission, fields=('vote_receiver',), extra=0)
