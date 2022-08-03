from django.utils.translation import ugettext as _

from ecs.notifications.forms import (
    NotificationForm, ProgressReportNotificationForm,
    CompletionReportNotificationForm, SingleStudyNotificationForm,
    AmendmentNotificationForm, SafetyNotificationForm,
    CenterCloseNotificationForm,
)


class Tab(object):
    def __init__(self, slug, label, fieldsets):
        self.slug = slug
        self.label = label
        self.fieldsets = fieldsets

    def __getitem__(self, index):
        # tabs used to be tuples, so we provide this for backwards compatibility.
        # string keys are required to make django templates happy.
        if isinstance(index, str):
            return getattr(self, index)
        if index == 0:
            return self.label
        if index == 1:
            return self.fieldsets
        raise IndexError


class NamedProxy(object):
    def __init__(self, data, name):
        self._data = data
        self._name = name

    def __getattr__(self, attr):
        if attr == 'name':
            return self._name
        return getattr(self._data, attr)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


SUBMISSION_FORM_TABS = (
    Tab('key_data', _('Key data'), [
        (_('type of project'), [
            'project_type_non_reg_drug', 'project_type_reg_drug', 'project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication', 'project_type_non_interventional_study',
            'project_type_medical_method', 'project_type_medical_device', 'project_type_medical_device_with_ce', 'project_type_medical_device_without_ce',
            'project_type_medical_device_performance_evaluation', 'project_type_basic_research', 'project_type_genetic_study', 'project_type_register',
            'project_type_biobank', 'project_type_retrospective', 'project_type_questionnaire', 'project_type_psychological_study', 'project_type_nursing_study',
            'project_type_gender_medicine',
            'submission_type', 'is_old_medtech',
            'project_type_misc', 'project_type_education_context', 'specialism', 'clinical_phase', 'already_voted',
        ]),
    ]),
    Tab('participants', _('participant'), [
        (_('test participant'), [
            'subject_count', 'subject_minage', 'subject_maxage', 'subject_males', 'subject_females_childbearing',
            'subject_noncompetents', 'subject_duration', 'subject_duration_active', 'subject_duration_controls', 'subject_planned_total_duration',
        ]),
    ]),
    Tab('outline', _('outline'), [
        (_('outline'), [
            'german_project_title', 'project_title',
            'german_summary', 'german_preclinical_results', 'german_primary_hypothesis', 'german_inclusion_exclusion_crit',
            'german_ethical_info', 'german_protected_subjects_info', 'german_recruitment_info', 'german_consent_info', 'german_risks_info',
            'german_benefits_info', 'german_relationship_info', 'german_concurrent_study_info', 'german_sideeffects_info',
            'german_statistical_info', 'german_dataprotection_info', 'german_aftercare_info', 'german_payment_info', 'german_abort_info', 'german_dataaccess_info',
            'german_financing_info', 'german_additional_info',
        ]),
    ]),
    Tab('sponsor', _('sponsor'), [
        (_('sponsor'), [
            'sponsor_name', # 1.5.1
            'sponsor_address', 'sponsor_zip_code', 'sponsor_city', # 1.5.2
            'sponsor_contact_gender', 'sponsor_contact_title', 'sponsor_contact_first_name', 'sponsor_contact_last_name', # 1.5.3
            'sponsor_phone', # 1.5.4
            'sponsor_fax', # 1.5.5
            'sponsor_email', # 1.5.6
            'sponsor_uid',
            'invoice_differs_from_sponsor',
        ]),
        (_('invoice recipient'), [
            'invoice_name',
            'invoice_address', 'invoice_zip_code', 'invoice_city',
            'invoice_contact_gender', 'invoice_contact_title', 'invoice_contact_first_name', 'invoice_contact_last_name',
            'invoice_phone', 'invoice_fax', 'invoice_email',
            'invoice_uid',
        ]),
    ]),
    Tab('applicant', _('applicant'), [
        (_('applicant'), [
            'submitter_contact_gender', 'submitter_contact_title', 'submitter_contact_first_name', 'submitter_contact_last_name', 'submitter_email',
            'submitter_organisation', 'submitter_jobtitle', 'submitter_is_coordinator', 'submitter_is_main_investigator', 'submitter_is_sponsor',
            'submitter_is_authorized_by_sponsor',
        ]),
    ]),
    Tab('amg', _('AMG'), [
        (_('drug trial'), ['eudract_number', 'pharma_checked_substance', 'pharma_reference_substance']),
        (_('AMG'), [
            'substance_registered_in_countries', 'substance_preexisting_clinical_tries',
            'substance_p_c_t_countries', 'substance_p_c_t_phase', 'substance_p_c_t_period',
            'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report',

        ]),
    ]),
    Tab('mpg', _('MPG'), [
        (_('Medical Device Study'), ['medtech_checked_product', 'medtech_reference_substance']),
        (_('MPG'), [
            'medtech_product_name', 'medtech_manufacturer', 'medtech_certified_for_exact_indications', 'medtech_certified_for_other_indications',
            'medtech_ce_symbol', 'medtech_manual_included', 'medtech_technical_safety_regulations', 'medtech_departure_from_regulations',
        ]),
    ]),
    Tab('measures', _('measures'), [
        ('', ['additional_therapy_info',]),
    ]),
    Tab('biometrics', _('biometrics'), [
        (_('biometrics'), [
            'study_plan_blind', 'study_plan_observer_blinded', 'study_plan_randomized', 'study_plan_parallelgroups', 'study_plan_controlled',
            'study_plan_cross_over', 'study_plan_placebo', 'study_plan_factorized', 'study_plan_pilot_project', 'study_plan_equivalence_testing',
            'study_plan_misc', 'study_plan_number_of_groups', 'study_plan_stratification', 'study_plan_sample_frequency', 'study_plan_primary_objectives',
            'study_plan_null_hypothesis', 'study_plan_alternative_hypothesis', 'study_plan_secondary_objectives',
        ]),
        (_('study plan'), [
            'study_plan_alpha', 'study_plan_alpha_sided', 'study_plan_power', 'study_plan_statalgorithm', 'study_plan_multiple_test', 'study_plan_multiple_test_correction_algorithm',
            'study_plan_dropout_ratio',
        ]),
        (_('planned statistical analysis'), [
            'study_plan_population_intention_to_treat', 'study_plan_population_per_protocol', 'study_plan_interim_evaluation', 'study_plan_abort_crit',
            'study_plan_planned_statalgorithm',
        ]),
        (_('documentation form / data management'), [
            'study_plan_dataquality_checking', 'study_plan_datamanagement',
        ]),
        (_('persons in charge'), [
            'study_plan_biometric_planning', 'study_plan_statistics_implementation',
        ]),
        (_('information privacy'), [
            'study_plan_dataprotection_choice', 'study_plan_dataprotection_reason', 'study_plan_dataprotection_dvr', 'study_plan_dataprotection_anonalgoritm',
        ]),
    ]),
    Tab('insurance', _('insurance'), [
        (_('insurance'), [
            'insurance_not_required',
            'insurance_name', 'insurance_address', 'insurance_phone', 'insurance_contract_number', 'insurance_validity',
        ]),
    ]),
    Tab('documents', _('documents'), []),
    Tab('centers', _('centres'), [
        (_('centers (non subject)'), NamedProxy([], 'centers_non_subject')),
        (_('centers abroad'), NamedProxy([], 'centers_abroad')),
    ]),
)

def get_all_used_submission_form_fields():
    all_fields = []
    for tab in SUBMISSION_FORM_TABS:
        for _, fields in tab.fieldsets:
            all_fields += fields
    return all_fields


NOTIFICATION_FORM_TABS = {}

NOTIFICATION_FORM_TABS[NotificationForm] = [
    Tab('general_information', _('General information'), [
        (_('General information'), [
            'submission_forms', 'comments',
        ]),
    ]),
    Tab('documents', _('documents'), []),
]

NOTIFICATION_FORM_TABS[SafetyNotificationForm] = [
    Tab('general_information', _('General information'), [
        (_('General information'), [
            'safety_type', 'submission_forms', 'comments',
        ]),
    ]),
    Tab('documents', _('documents'), []),
]

NOTIFICATION_FORM_TABS[SingleStudyNotificationForm] = [
    Tab('general_information', _('General information'), [
        (_('General information'), [
            'submission_form', 'comments',
        ]),
    ]),
    Tab('documents', _('documents'), []),
]

NOTIFICATION_FORM_TABS[AmendmentNotificationForm] = [
    Tab('general_information', _('General information'), [
        (_('General information'), [
            'comments',
        ]),
    ]),
    Tab('changes', _('Made Changes'), [])
]


NOTIFICATION_FORM_TABS[CompletionReportNotificationForm] = NOTIFICATION_FORM_TABS[SingleStudyNotificationForm][:1] + [
    Tab('study_status', _('Study status'), [
        ('Status', [
            'study_started', 'reason_for_not_started', 'study_aborted', 'completion_date',
        ]),
        (_('participants'), [
            'recruited_subjects', 'finished_subjects', 'aborted_subjects',
        ]),
        (_('SAE / SUSAR'), [
            'SAE_count', 'SUSAR_count',
        ])
    ]),
    Tab('documents', _('documents'), []),
]

NOTIFICATION_FORM_TABS[ProgressReportNotificationForm] = [
    Tab('general_information', _('General information'), [
        (_('General information'), [
            'submission_form', 'comments',
        ]),
    ]),
    Tab('study_status', _('Study status'), [
        (_('Status'), [
            'study_started', 'reason_for_not_started', 'runs_till',
        ]),
        (_('participants'), [
            'recruited_subjects', 'finished_subjects', 'aborted_subjects',
        ]),
        ('SAE / SUSAR', [
            'SAE_count', 'SUSAR_count',
        ]),
    ]),
    Tab('documents', _('documents'), []),
]

NOTIFICATION_FORM_TABS[CenterCloseNotificationForm] = [
    Tab('general_information', _('General information'), [
        (_('General information'), [
            'submission_form', 'investigator', 'close_date', 'comments',
        ]),
    ]),
    Tab('documents', _('documents'), []),
]

def get_notification_form_tabs(form_cls):
    for cls in form_cls.__mro__:
        try:
            return NOTIFICATION_FORM_TABS[cls]
        except KeyError:
            pass
    return []
