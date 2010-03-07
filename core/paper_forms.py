# -*- coding: utf-8 -*-
from django.db.models import FieldDoesNotExist
from ecs.core.models import SubmissionForm

SUBMISSION_SECTION_DATA = [
    ('1.', u'Allgemeines', u''),
    ('2.', u'Eckdaten der Studie', u''),
    ('3a', u'Betrifft nur Studien gemäß AMG: Angaben zur Prüfsubstanz (falls nicht in Österreich registriert):', u''),
]

_submission_field_data = (
    ('1.1', 'project_title', u''),
    ('1.2', None, u''), #'protocol_number'
    ('1.3', None, u''), #'date_of_protocol'
    ('1.2.1', 'eudract_number', u''),
    ('1.3.1', None, u''), #'isrctn_number'
    ('1.5.1', 'sponsor_name', u''),
    ('1.5.3', 'sponsor_contactname', u''),
    ('1.5.2', 'sponsor_address1', u''),
    ('1.5.2', 'sponsor_address2', u''),
    ('1.5.2', 'sponsor_zip_code', u''),
    ('1.5.2', 'sponsor_city', u''),
    ('1.5.4', 'sponsor_phone', u''),
    ('1.5.5', 'sponsor_fax', u''),
    ('1.5.6', 'sponsor_email', u''),
    ('1.5.1', 'invoice_name', u''),
    ('1.5.3', 'invoice_contactname', u''),
    ('1.5.2', 'invoice_address1', u''),
    ('1.5.2', 'invoice_address2', u''),
    ('1.5.2', 'invoice_zip_code', u''),
    ('1.5.2', 'invoice_city', u''),
    ('1.5.4', 'invoice_phone', u''),
    ('1.5.5', 'invoice_fax', u''),
    ('1.5.6', 'invoice_email', u''),
    ('1.5.7', 'invoice_uid', u''),
    (None, 'invoice_uid_verified_level1', u''),
    (None, 'invoice_uid_verified_level2', u''),
    ('2.1.1', 'project_type_non_reg_drug', u''),
    ('2.1.2', 'project_type_reg_drug', u''),
    ('2.1.2.1', 'project_type_reg_drug_within_indication', u''),
    ('2.1.2.2', 'project_type_reg_drug_not_within_indication', u''),
    ('2.1.3', 'project_type_medical_method', u''),
    ('2.1.4', 'project_type_medical_device', u''),
    ('2.1.4.1', 'project_type_medical_device_with_ce', u''),
    ('2.1.4.2', 'project_type_medical_device_without_ce', u''),
    ('2.1.4.3', 'project_type_medical_device_performance_evaluation', u''),
    ('2.1.5', 'project_type_basic_research', u''),
    ('2.1.6', 'project_type_genetic_study', u''),
    ('2.1.7', 'project_type_register', u''), # new
    ('2.1.8', 'project_type_biobank', u''), # new
    ('2.1.9', 'project_type_retrospective', u''), # new
    ('2.1.10', 'project_type_questionnaire', u''), # new
    ('2.1.11', 'project_type_misc', u''), # was: 2.17
    ('2.1.12', 'project_type_education_context', u''), # was: 2.1.8 + 2.1.9
    ('2.2', 'specialism', u''),
    ('2.3.1', 'pharma_checked_substance', u''),
    ('2.3.2', 'pharma_reference_substance', u''),
    ('2.4.1', 'medtech_checked_product', u''),
    ('2.4.2', 'medtech_reference_substance', u''),
    ('2.5', 'clinical_phase', u''),
    ('2.8', 'already_voted', u''),
    ('2.9', 'subject_count', u''),
    ('2.10.1', 'subject_minage', u''),
    ('2.10.2', 'subject_maxage', u''),
    ('2.10.3', 'subject_noncompetents', u''),
    ('2.10.4', 'subject_males', u''),
    ('2.10.4', 'subject_females', u''),
    ('2.10.5', 'subject_childbearing', u''),
    ('2.11', 'subject_duration', u''),
    ('2.11.1', 'subject_duration_active', u''),
    ('2.11.2', 'subject_duration_controls', u''),
    ('2.12', 'subject_planned_total_duration', u''),
    ('3.1', 'substance_registered_in_countries', u''),
    ('3.2', 'substance_preexisting_clinical_tries', u''),
    ('3.2.1', 'substance_p_c_t_countries', u''),
    ('3.2.2', 'substance_p_c_t_phase', u''),
    ('3.2.3', 'substance_p_c_t_period', u''),
    ('3.2.4', 'substance_p_c_t_application_type', u''),
    ('3.2.5', 'substance_p_c_t_gcp_rules', u''),
    ('3.2.6', 'substance_p_c_t_final_report', u''),
    ('4.1', 'medtech_product_name', u''),
    ('4.2', 'medtech_manufacturer', u''),
    ('4.3', 'medtech_certified_for_exact_indications', u''),
    ('4.4', 'medtech_certified_for_other_indications', u''),
    ('4.5', 'medtech_ce_symbol', u''),
    ('4.6', 'medtech_manual_included', u''),
    ('4.7', 'medtech_technical_safety_regulations', u''),
    ('4.8', 'medtech_departure_from_regulations', u''),
    ('5.1.1', 'insurance_name', u''),
    ('5.1.2', 'insurance_address_1', u''),
    ('5.1.3', 'insurance_phone', u''),
    ('5.1.4', 'insurance_contract_number', u''),
    ('5.1.5', 'insurance_validity', u''),
    ('6.3', 'additional_therapy_info', u''),
    ('7.1', 'german_project_title', u''),
    ('7.2', 'german_summary', u''),
    ('7.3', 'german_preclinical_results', u''),
    ('7.4', 'german_primary_hypothesis', u''),
    ('7.5', 'german_inclusion_exclusion_crit', u''),
    ('7.6', 'german_ethical_info', u''),
    ('7.7', 'german_protected_subjects_info', u''),
    ('7.8', 'german_recruitment_info', u''),
    ('7.9', 'german_consent_info', u''),
    ('7.10', 'german_risks_info', u''),
    ('7.11', 'german_benefits_info', u''),
    ('7.12', 'german_relationship_info', u''),
    ('7.13', 'german_concurrent_study_info', u''),
    ('7.14', 'german_sideeffects_info', u''),
    ('7.15', 'german_statistical_info', u''),
    ('7.16', 'german_dataprotection_info', u''),
    ('7.17', 'german_aftercare_info', u''),
    ('7.18', 'german_payment_info', u''),
    ('7.19', 'german_abort_info', u''),
    ('7.20', 'german_dataaccess_info', u''),
    ('7.21', 'german_financing_info', u''),
    ('7.22', 'german_additional_info', u''),
    ('8.1.1', 'study_plan_open', u'offen'), # property
    ('8.1.2', 'study_plan_randomized', u'randomisiert'),
    ('8.1.3', 'study_plan_parallelgroups', u'Parallelgruppen'),
    ('8.1.4', 'monocentric', u'monozentrisch'), # property
    ('8.1.5', 'study_plan_single_blind', u'blind'), # property
    ('8.1.6', 'study_plan_controlled', u'kontrolliert'),
    ('8.1.7', 'study_plan_cross_over', u'cross-over'),
    ('8.1.8', 'multicentric', u'multizentrisch'), # property
    ('8.1.9', 'study_plan_double_blind', u'doppelblind'), # property
    ('8.1.10', 'study_plan_placebo', u'Placebo'),
    ('8.1.11', 'study_plan_factorized', u'faktoriell'),
    ('8.1.12', 'study_plan_pilot_project', u'Pilotprojekt'),
    ('8.1.13', 'study_plan_observer_blinded', u'observer-blinded'),
    ('8.1.14', 'study_plan_equivalence_testing', u'Äquivalenzprüfung'),
    ('8.1.15', 'study_plan_misc', u'Sonstiges'),
    ('8.1.16', 'study_plan_number_of_groups', u'Anzahl der Gruppen'),
    ('8.1.17', 'study_plan_stratification', u'Stratifizierung'),
    ('8.1.18', 'study_plan_sample_frequency', u'Messwiederholungen'),
    ('8.1.19', 'study_plan_primary_objectives', u'Hauptzielgröße'),
    ('8.1.20', 'study_plan_null_hypothesis', u'Nullhypothese(n)'),
    ('8.1.21', 'study_plan_alternative_hypothesis', u'Alternativhypothese(n)'),
    ('8.1.22', 'study_plan_secondary_objectives', u'Nebenzielgrößen'),
    ('8.2.1', 'study_plan_alpha', u'Alpha'),
    ('8.2.2', 'study_plan_power', u'Power'),
    ('8.2.3', 'study_plan_statalgorithm', u'Stat.Verfahren'),
    ('8.2.4', 'study_plan_multiple_test_correction_algorithm', u'Multiples Testen, Korrekturverfahren'),
    ('8.2.5', 'study_plan_dropout_ratio', u'Erwartete Anzahl von Studienabbrecher/inne/n (Drop-out-Quote)'),
    ('8.3.1', 'study_plan_population_intention_to_treat', u'Intention-to-treat'),
    ('8.3.2', 'study_plan_population_per_protocol', u'Per Protocol'),
    ('8.3.3', 'study_plan_abort_crit', u''),
    ('8.3.4', 'study_plan_planned_statalgorithm', u'Geplante statistische Verfahren'),
    ('8.4.1', 'study_plan_dataquality_checking', u'Angaben zur Datenqualitätsprüfung'),
    ('8.4.2', 'study_plan_datamanagement', u'Angaben zum Datenmanagement'),
    ('8.5.1', 'study_plan_biometric_planning', u'Wer führte die biometrische Planung durch (ggf. Nachweis der Qualifikation)?'),
    ('8.5.2', 'study_plan_statistics_implementation', u'Wer wird die statistische Auswertung durchführen (ggf. Nachweis der Qualifikation)?'),
    ('8.6.2', 'study_plan_dataprotection_reason', u''),
    ('8.6.2', 'study_plan_dataprotection_dvr', u''),
    ('8.6.3', 'study_plan_dataprotection_anonalgoritm', u'Wie erfolgt die Anonymisierung?'),
    ('9.1', 'submitter_name', u''),
    ('9.2', 'submitter_organisation', u''),
    ('9.3', 'submitter_jobtitle', u''),
    ('9.4.1', 'submitter_is_coordinator', u''),
    ('9.4.2', 'submitter_is_main_investigator', u''),
    ('9.4.3', 'submitter_is_sponsor', u''),
    ('9.4.4', 'submitter_is_authorized_by_sponsor', u''),
    (None, 'submitter_agrees_to_publishing', u''),
)

_numbers_by_fieldname = {} 

SUBMISSION_FIELD_DATA = []
for number, field_name, label in _submission_field_data:
    if not label:
        try:
            label = SubmissionForm._meta.get_field(field_name).verbose_name
        except FieldDoesNotExist:
            label = None
    if field_name:
        _numbers_by_fieldname[field_name] = number
    SUBMISSION_FIELD_DATA.append((number, label, field_name))
    
    
def get_number_for_fieldname(name):
    return _numbers_by_fieldname[name]
    
