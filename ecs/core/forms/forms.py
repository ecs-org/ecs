import logging
from datetime import timedelta
from functools import reduce

from django import forms
from django.forms.formsets import BaseFormSet, formset_factory
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from django_countries import countries

from ecs.core.models import (
    Investigator, InvestigatorEmployee, SubmissionForm, Measure,
    ParticipatingCenterNonSubject, ForeignParticipatingCenter,
    NonTestedUsedDrug, Submission, TemporaryAuthorization, AdvancedSettings,
    EthicsCommission,
)

from ecs.utils.formutils import require_fields
from ecs.core.forms.fields import StrippedTextInput, NullBooleanField, \
    EmailUserSelectWidget, AutocompleteModelChoiceField, DateTimeField
from ecs.core.forms.utils import ReadonlyFormMixin, ReadonlyFormSetMixin
from ecs.users.utils import get_current_user
from ecs.tags.forms import TagMultipleChoiceField


## submissions ##

AMG_REQUIRED_FIELDS = (
    'substance_preexisting_clinical_tries', 'submission_type', 'eudract_number',
    'pharma_checked_substance', 'pharma_reference_substance',
)
AMG_FIELDS = AMG_REQUIRED_FIELDS + ('substance_registered_in_countries', 'substance_p_c_t_countries','substance_p_c_t_phase', 'substance_p_c_t_period',
    'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report',)

MPG_NEW_LAW_FIELDS = (
    'medtech_is_new_law',
    'submission_type',
)

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

class SubmissionFormForm(ReadonlyFormMixin, forms.ModelForm):
    substance_preexisting_clinical_tries = NullBooleanField(required=False)
    substance_p_c_t_gcp_rules = NullBooleanField(required=False)
    substance_p_c_t_final_report = NullBooleanField(required=False)
    substance_registered_in_countries = forms.MultipleChoiceField(
        choices=countries, required=False)
    substance_p_c_t_countries = forms.MultipleChoiceField(
        choices=countries, required=False)

    medtech_certified_for_exact_indications = NullBooleanField(required=False)
    medtech_certified_for_other_indications = NullBooleanField(required=False)
    medtech_ce_symbol = NullBooleanField(required=False)
    medtech_manual_included = NullBooleanField(required=False)

    subject_males = NullBooleanField()
    subject_females_childbearing = forms.ChoiceField(choices=(
        (None, '-'),
        ('0', _('Yes, also childbearing')),
        ('1', _('Yes, but no childbearing')),
        ('2', _('Yes, but only childbearing')),
        ('3', _('No')),
    ))

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

            'subject_count', 'subject_minage', 'subject_maxage', 'subject_noncompetents', 'subject_males', 'subject_females_childbearing',
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
        ) + AMG_FIELDS + MPG_NEW_LAW_FIELDS + MPG_FIELDS + INSURANCE_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.EmailField):
                field.widget = StrippedTextInput()
                if self.readonly:
                    field.widget.attrs['readonly'] = 'readonly'
                    field.widget.attrs['placeholder'] = \
                        '-- {0} --'.format(_('No information given'))

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['project_type_reg_drug'] = any(self.cleaned_data.get(f, False) for f in ('project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication'))
        cleaned_data['project_type_medical_device'] = any(self.cleaned_data.get(f, False) for f in ('project_type_medical_device_with_ce', 'project_type_medical_device_without_ce', 'project_type_medical_device_performance_evaluation'))

        if any(cleaned_data.get(f, False) for f in ('project_type_reg_drug', 'project_type_non_reg_drug')):
            require_fields(self, AMG_REQUIRED_FIELDS)

        if cleaned_data.get('project_type_medical_device', False):
            require_fields(self, MPG_FIELDS)
            if cleaned_data.get('medtech_is_new_law', False):
                require_fields(self, MPG_NEW_LAW_FIELDS)

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

        require_fields(self, ('subject_males',))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.subject_females, instance.subject_childbearing = (
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        )[int(self.cleaned_data['subject_females_childbearing'])]
        if commit:
            instance.save()
            self.save_m2m()
        return instance


## ##

class ParticipatingCenterNonSubjectForm(forms.ModelForm):
    ethics_commission = forms.ModelChoiceField(
        EthicsCommission.objects.order_by('name'), required=True)

    class Meta:
        model = ParticipatingCenterNonSubject
        fields = ('name', 'ethics_commission', 'investigator_name')

class ReadonlyBaseFormSet(ReadonlyFormSetMixin, BaseFormSet):
    def save(self, commit=True):
        return [
            form.save(commit=commit) for form in self.forms
            if form.is_valid() and form.has_changed()
        ]

ParticipatingCenterNonSubjectFormSet = formset_factory(
    ParticipatingCenterNonSubjectForm, formset=ReadonlyBaseFormSet, extra=0)

class ForeignParticipatingCenterForm(forms.ModelForm):
    class Meta:
        model = ForeignParticipatingCenter
        exclude = ('submission_form',)

ForeignParticipatingCenterFormSet = formset_factory(
    ForeignParticipatingCenterForm, formset=ReadonlyBaseFormSet, extra=0)

class NonTestedUsedDrugForm(forms.ModelForm):
    class Meta:
        model = NonTestedUsedDrug
        exclude = ('submission_form',)

NonTestedUsedDrugFormSet = formset_factory(NonTestedUsedDrugForm,
    formset=ReadonlyBaseFormSet, extra=0)

class MeasureForm(forms.ModelForm):
    category = forms.CharField(widget=forms.HiddenInput(), initial='6.1')

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
    category = forms.CharField(widget=forms.HiddenInput(), initial='6.2')

MeasureFormSet = formset_factory(MeasureForm, formset=ReadonlyBaseFormSet,
    extra=0)
RoutineMeasureFormSet = formset_factory(RoutineMeasureForm,
    formset=ReadonlyBaseFormSet, extra=0)

class InvestigatorForm(forms.ModelForm):
    ethics_commission = forms.ModelChoiceField(
        EthicsCommission.objects.order_by('name'), required=True)

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
        super().__init__(*args, **kwargs)
        if get_current_user().profile.is_internal:
            self.fields['presenter'] = AutocompleteModelChoiceField(
                'users', User.objects.filter(is_active=True),
                label=_('Presenter'))

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
        super().__init__(*args, **kwargs)
        if get_current_user().profile.is_internal:
            self.fields['susar_presenter'] = AutocompleteModelChoiceField(
                'users', User.objects.filter(is_active=True),
                label=_('Susar Presenter'))

class BaseInvestigatorFormSet(ReadonlyFormSetMixin, BaseFormSet):
    def save(self, commit=True):
        return [
            form.save(commit=commit)
            for form in self.forms[:self.total_form_count()]
            if form.is_valid() and form.has_changed()
        ]

    def clean(self):
        super().clean()
        changed_forms = [
            form for form in self.forms[:self.total_form_count()]
            if form.is_valid() and form.has_changed()
        ]
        if len(changed_forms) < 1:
            raise forms.ValidationError(_('At least one centre is required.'))

        if any(self.errors):
            return
        elif not len([f for f in self.forms[:self.total_form_count()] if f.cleaned_data.get('main', False)]) == 1:
            raise forms.ValidationError(_('Please select exactly one primary investigator.'))

InvestigatorFormSet = formset_factory(InvestigatorForm,
    formset=BaseInvestigatorFormSet)

class InvestigatorEmployeeForm(forms.ModelForm):
    investigator_index = forms.IntegerField(required=True, initial=0, widget=forms.HiddenInput())

    class Meta:
        model = InvestigatorEmployee
        exclude = ('investigator',)

    def has_changed(self):
        return bool(set(self.changed_data) - set(('investigator_index',)))

    def save(self, commit=True):
        instance = super(InvestigatorEmployeeForm, self).save(commit=commit)
        instance.investigator_index = self.cleaned_data['investigator_index']
        return instance

class BaseInvestigatorEmployeeFormSet(ReadonlyFormSetMixin, BaseFormSet):
    def save(self, commit=True):
        return [
            form.save(commit=commit)
            for form in self.forms[:self.total_form_count()]
            if form.is_valid() and form.has_changed()
        ]

InvestigatorEmployeeFormSet = formset_factory(InvestigatorEmployeeForm,
    formset=BaseInvestigatorEmployeeFormSet)


_queries = {
    'past_meetings':    lambda s,u: s.past_meetings(),
    'next_meeting':     lambda s,u: s.next_meeting(),
    'upcoming_meetings':lambda s,u: s.upcoming_meetings().exclude(pk__in=s.next_meeting().values('pk')),
    'no_meeting':       lambda s,u: s.no_meeting(),

    'mine':             lambda s,u: s.mine(u),
    'assigned':         lambda s,u: s.reviewed_by_user(u),
    'other_studies':    lambda s,u: s.exclude(pk__in=s.mine(u).values('pk')).exclude(pk__in=s.reviewed_by_user(u).values('pk')),
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
        newcls = super().__new__(cls, name, bases, attrs)
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
        return super().__init__(data, *args, **kwargs)

    def _filter_by_type(self, submissions, user):
        qs = []
        if self.cleaned_data['amg']:
            qs.append(
                Q(current_submission_form__project_type_non_reg_drug=True) |
                Q(current_submission_form__project_type_reg_drug=True)
            )
        if self.cleaned_data['mpg']:
            qs.append(Q(current_submission_form__project_type_medical_device=True))
        if self.cleaned_data['other']:
            qs.append(
                Q(current_submission_form__project_type_non_reg_drug=False) &
                Q(current_submission_form__project_type_reg_drug=False) &
                Q(current_submission_form__project_type_medical_device=False)
            )
        return submissions.filter(reduce(lambda x, y: x | y, qs))

    def _filter_by_lane(self, submissions, user):
        from ecs.core.models.constants import (
            SUBMISSION_LANE_EXPEDITED, SUBMISSION_LANE_LOCALEC,
            SUBMISSION_LANE_RETROSPECTIVE_THESIS, SUBMISSION_LANE_BOARD
        )
        lanes = []
        if self.cleaned_data['board']:
            lanes.append(SUBMISSION_LANE_BOARD)
        if self.cleaned_data['thesis']:
            lanes.append(SUBMISSION_LANE_RETROSPECTIVE_THESIS)
        if self.cleaned_data['expedited']:
            lanes.append(SUBMISSION_LANE_EXPEDITED)
        if self.cleaned_data['local_ec']:
            lanes.append(SUBMISSION_LANE_LOCALEC)
        new = submissions.filter(workflow_lane__in=lanes)
        if self.cleaned_data['not_categorized']:
            new |= submissions.filter(workflow_lane=None)
        return new

    def _filter_by_votes(self, submissions, user):
        results = []
        if self.cleaned_data['b2']:
            results.append('2')
        if self.cleaned_data['b3']:
            results += ['3a', '3b']
        if self.cleaned_data['other_votes']:
            results += ['1', '4', '5']

        qs = []
        if results:
            q = Q(current_published_vote__result__in=results)
            if user.profile.is_internal:
                q |= Q(current_pending_vote__result__in=results)
            qs.append(q)

        if self.cleaned_data['no_votes']:
            q = Q(current_published_vote=None)
            if user.profile.is_internal:
                q &= Q(current_pending_vote=None)
            qs.append(q & Q(current_submission_form__isnull=False))

        return submissions.filter(reduce(lambda x, y: x | y, qs))

    def filter_submissions(self, submissions, user):
        self.is_valid()   # force clean

        for row in self.layout:
            active = sum(1 for f in row if self.cleaned_data[f])
            if not active:
                return submissions.none()
            elif active != len(row):
                if row == FILTER_TYPE:
                    submissions = self._filter_by_type(submissions, user)
                elif row == FILTER_LANE:
                    submissions = self._filter_by_lane(submissions, user)
                elif row == FILTER_VOTES:
                    submissions = self._filter_by_votes(submissions, user)
                else:
                    new = submissions.none()
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

class AssignedSubmissionsFilterForm(SubmissionFilterForm):
    layout = (FILTER_MEETINGS, FILTER_LANE, FILTER_TYPE, FILTER_VOTES)

class AllSubmissionsFilterForm(SubmissionFilterForm):
    layout = (FILTER_MEETINGS, FILTER_LANE, FILTER_TYPE, FILTER_VOTES, FILTER_ASSIGNMENT)
    tags = TagMultipleChoiceField(label=_('Tags'), required=False)

    def filter_submissions(self, submissions, user):
        submissions = super().filter_submissions(submissions, user)
        if self.cleaned_data.get('tags'):
            submissions = submissions.filter(tags__in=self.cleaned_data['tags'])
        return submissions


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

class TemporaryAuthorizationForm(forms.ModelForm):
    start = DateTimeField(initial=timezone.now, label=_('Start'))
    end = DateTimeField(initial=lambda: timezone.now() + timedelta(days=30),
        label=_('End'))
    user = AutocompleteModelChoiceField('users', User.objects.all(),
        label=_('User'))

    class Meta:
        model = TemporaryAuthorization
        exclude = ('submission',)

class AdvancedSettingsForm(forms.ModelForm):
    default_contact = AutocompleteModelChoiceField(
        'internal-users', User.objects.all(), label=_('Default Contact'))

    LOGO_MIMETYPES = ('image/gif', 'image/jpeg', 'image/png', 'image/svg+xml')

    logo_file = forms.FileField(required=False, label=_('Change Logo File'),
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))
    print_logo_file = forms.FileField(required=False,
        label=_('Change Print Logo File'),
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))

    def clean_logo_file(self):
        f = self.cleaned_data['logo_file']
        if f and f.content_type not in self.LOGO_MIMETYPES:
            self.add_error('logo_file',
                _('The file must be a gif, jpeg, png or svg file.'))
        return f

    def clean_print_logo_file(self):
        f = self.cleaned_data['print_logo_file']
        if f and f.content_type not in self.LOGO_MIMETYPES:
            self.add_error('print_logo_file',
                _('The file must be a gif, jpeg, png or svg file.'))
        return f

    class Meta:
        model = AdvancedSettings
        fields = (
            'default_contact', 'display_notifications_in_protocol',
            'display_biased_in_amendment_answer_pdf',
            'require_internal_vote_review', 'logo_file', 'print_logo_file',
            'address', 'meeting_address', 'contact_email', 'contact_url',
            'member_list_url', 'signature_block',
            'vote1_extra', 'vote2_extra', 'vote3a_extra', 'vote3b_extra',
            'vote4_extra', 'vote5_extra', 'vote_pdf_extra',
        )
        labels = {
            'display_notifications_in_protocol':
                _('Display Notifications in Protocol'),
            'display_biased_in_amendment_answer_pdf':
                _('Display biased board member in amendment answer PDF'),
            'require_internal_vote_review': _('Require internal vote review'),
            'address': _('address'),
            'meeting_address': _('Meeting Address'),
            'contact_email': _('Contact Email'),
            'contact_url': _('Contact URL'),
            'member_list_url': _('Member List URL'),
            'signature_block': _('Signature Block'),
            'vote1_extra': _('Vote Result 1 Extra Text'),
            'vote2_extra': _('Vote Result 2 Extra Text'),
            'vote3a_extra': _('Vote Result 3a Extra Text'),
            'vote3b_extra': _('Vote Result 3b Extra Text'),
            'vote4_extra': _('Vote Result 4 Extra Text'),
            'vote5_extra': _('Vote Result 5 Extra Text'),
            'vote_pdf_extra': _('Vote PDF Extra Text'),
        }

EthicsCommissionFormSet = modelformset_factory(EthicsCommission, fields=('vote_receiver',), extra=0)
