# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _

from ecs.core.forms.forms import NotificationForm, ProgressReportNotificationForm, CompletionReportNotificationForm, SingleStudyNotificationForm, AmendmentNotificationForm

# ((tab_label1, [(fieldset_legend11, [field111, field112, ..]), (fieldset_legend12, [field121, field122, ..]), ...]),
#  (tab_label2, [(fieldset_legend21, [field211, field212, ..]), (fieldset_legend22, [field221, field222, ..]), ...]),
# )

SUBMISSION_FORM_TABS = (
    (_(u'Key data'), [
        (_(u'type of project'), [
            'project_type_non_reg_drug', 'project_type_reg_drug', 'project_type_reg_drug_within_indication', 'project_type_reg_drug_not_within_indication', 
            'project_type_medical_method', 'project_type_medical_device', 'project_type_medical_device_with_ce', 'project_type_medical_device_without_ce',
            'project_type_medical_device_performance_evaluation', 'project_type_basic_research', 'project_type_genetic_study', 'project_type_register',
            'project_type_biobank', 'project_type_retrospective', 'project_type_questionnaire', 'project_type_psychological_study', 'project_type_nursing_study',
            'project_type_education_context', 'project_type_misc',
            'specialism', 'clinical_phase', 'external_reviewer_suggestions', 'already_voted',
        ]),
    ]),
    (_(u'participant'), [
        (_(u'test participant'), [
            'subject_count', 'subject_minage', 'subject_maxage', 'subject_noncompetents', 'subject_males', 'subject_females', 
            'subject_childbearing', 'subject_duration', 'subject_duration_active', 'subject_duration_controls', 'subject_planned_total_duration',
        ]),
        (_(u'centers abroad'), []),
    ]),
    (_(u'outline'), [
        (_(u'outline'), [
            'project_title', 'german_project_title', 'protocol_number',
            'german_summary', 'german_preclinical_results', 'german_primary_hypothesis', 'german_inclusion_exclusion_crit', 
            'german_ethical_info', 'german_protected_subjects_info', 'german_recruitment_info', 'german_consent_info', 'german_risks_info', 
            'german_benefits_info', 'german_relationship_info', 'german_concurrent_study_info', 'german_sideeffects_info', 
            'german_statistical_info', 'german_dataprotection_info', 'german_aftercare_info', 'german_payment_info', 'german_abort_info', 'german_dataaccess_info',
            'german_financing_info', 'german_additional_info',
        ]),
    ]),
    (_(u'sponsor'), [
        (_(u'sponsor'), [
            'sponsor_name', # 1.5.1
            'sponsor_address', 'sponsor_zip_code', 'sponsor_city', # 1.5.2
            'sponsor_contact_gender', 'sponsor_contact_title', 'sponsor_contact_first_name', 'sponsor_contact_last_name', # 1.5.3
            'sponsor_phone', # 1.5.4
            'sponsor_fax', # 1.5.5
            'sponsor_email', # 1.5.6
            'sponsor_agrees_to_publishing',
            'invoice_differs_from_sponsor',
        ]),
        (_(u'invoice recipient'), [
            'invoice_name', 
            'invoice_contact_gender', 'invoice_contact_title', 'invoice_contact_first_name', 'invoice_contact_last_name',
            'invoice_address', 'invoice_zip_code', 
            'invoice_city', 'invoice_phone', 'invoice_fax', 'invoice_email',
            'invoice_uid_verified_level1', 'invoice_uid_verified_level2',
        ]),
    ]),
    (_(u'applicant'), [
        (_(u'applicant'), [
            'submitter_contact_gender', 'submitter_contact_title', 'submitter_contact_first_name', 'submitter_contact_last_name', 'submitter_email',
            'submitter_organisation', 'submitter_jobtitle', 'submitter_is_coordinator', 'submitter_is_main_investigator', 'submitter_is_sponsor',
            'submitter_is_authorized_by_sponsor', 
        ]),
    ]),
    (_(u'AMG'), [
        (_(u'drug trial'), ['eudract_number', 'pharma_checked_substance', 'pharma_reference_substance']),
        (_(u'AMG'), [
            'substance_registered_in_countries', 'substance_preexisting_clinical_tries', 
            'substance_p_c_t_countries', 'substance_p_c_t_phase', 'substance_p_c_t_period', 
            'substance_p_c_t_application_type', 'substance_p_c_t_gcp_rules', 'substance_p_c_t_final_report',
            'submission_type',
        ]),
    ]),
    (_(u'MPG'), [
        (_(u'Medical Device Study'), ['medtech_checked_product', 'medtech_reference_substance']),    
        (_(u'MPG'), [
            'medtech_product_name', 'medtech_manufacturer', 'medtech_certified_for_exact_indications', 'medtech_certified_for_other_indications', 
            'medtech_ce_symbol', 'medtech_manual_included', 'medtech_technical_safety_regulations', 'medtech_departure_from_regulations',
        ]),
    ]),
    (_(u'measures'), [
        (u'', ['additional_therapy_info',]),
    ]),
    (_(u'biometrics'), [
        (_(u'biometrics'), [
            'study_plan_blind', 'study_plan_observer_blinded', 'study_plan_randomized', 'study_plan_parallelgroups', 'study_plan_controlled',
            'study_plan_cross_over', 'study_plan_placebo', 'study_plan_factorized', 'study_plan_pilot_project', 'study_plan_equivalence_testing',
            'study_plan_misc', 'study_plan_number_of_groups', 'study_plan_stratification', 'study_plan_sample_frequency', 'study_plan_primary_objectives',
            'study_plan_null_hypothesis', 'study_plan_alternative_hypothesis', 'study_plan_secondary_objectives',
        ]),
        (_(u'study plan'), [
            'study_plan_alpha', 'study_plan_power', 'study_plan_statalgorithm', 'study_plan_multiple_test', 'study_plan_multiple_test_correction_algorithm',
            'study_plan_dropout_ratio',
        ]),
        (_(u'planned statistical analysis'), [
            'study_plan_population_intention_to_treat', 'study_plan_population_per_protocol', 'study_plan_interim_evaluation', 'study_plan_abort_crit',
            'study_plan_planned_statalgorithm',
        ]),
        (_(u'documentation form / data management'), [
            'study_plan_dataquality_checking', 'study_plan_datamanagement',
        ]),
        (_(u'persons in charge'), [
            'study_plan_biometric_planning', 'study_plan_statistics_implementation',
        ]),
        (_(u'information privacy'), [
            'study_plan_dataprotection_choice', 'study_plan_dataprotection_reason', 'study_plan_dataprotection_dvr', 'study_plan_dataprotection_anonalgoritm', 
        ]),
    ]),
    (_(u'insurance'), [
        (_(u'insurance'), [
            'insurance_name', 'insurance_address', 'insurance_phone', 'insurance_contract_number', 'insurance_validity',
        ]),
    ]),
    (_(u'documents'), []),
    (_(u'centres'), []),
)

def get_all_used_submission_form_fields():
    all_fields = []
    for _, fieldsets in SUBMISSION_FORM_TABS:
        for _, fields in fieldsets:
            all_fields += fields
    return all_fields


NOTIFICATION_FORM_TABS = {}

NOTIFICATION_FORM_TABS[NotificationForm] = [
    (_(u'General information'), [
        (_(u'General information'), [
            'submission_forms', 'comments',
        ]),
    ]),
    (_(u'documents'), []),
]

NOTIFICATION_FORM_TABS[SingleStudyNotificationForm] = [
    (_(u'General information'), [
        (_(u'General information'), [
            'submission_form', 'comments',
        ]),
    ]),
    (_(u'documents'), []),
]

NOTIFICATION_FORM_TABS[AmendmentNotificationForm] = [
    (_(u'General information'), [
        (_(u'General information'), [
            'comments',
        ]),
    ]),
    (_(u'Changes'), [])
]


NOTIFICATION_FORM_TABS[CompletionReportNotificationForm] = NOTIFICATION_FORM_TABS[SingleStudyNotificationForm][:1] + [
    (_(u'Study status'), [
        (u'status', [
            'reason_for_not_started', 'study_aborted', 'completion_date',
        ]),
        (u'participant', [
            'recruited_subjects', 'finished_subjects', 'aborted_subjects',
        ]),
        (u'SAE / SUSAR', [
            'SAE_count', 'SUSAR_count',
        ])
    ]),
    (_(u'documents'), []),
]

NOTIFICATION_FORM_TABS[ProgressReportNotificationForm] = [
    (_(u'General information'), [
        (_(u'General information'), [
            'submission_form', 'extension_of_vote_requested', 'comments',
        ]),
    ]),
    (_(u'Study status'), [
        (_(u'Status'), [
            'reason_for_not_started', 'runs_till',
        ]),
        (_(u'participants'), [
            'recruited_subjects', 'finished_subjects', 'aborted_subjects',
        ]),
        (u'SAE / SUSAR', [
            'SAE_count', 'SUSAR_count',
        ]),
    ]),
    (_(u'documents'), []),
]

def get_notification_form_tabs(form_cls):
    for cls in form_cls.__mro__:
        try:
            return NOTIFICATION_FORM_TABS[cls]
        except KeyError:
            pass
    return []
