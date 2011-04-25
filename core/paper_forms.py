# -*- coding: utf-8 -*-
from django.utils.functional import memoize

from ecs.core.models import Submission, SubmissionForm, ForeignParticipatingCenter, Measure, NonTestedUsedDrug, Investigator, InvestigatorEmployee
from ecs.notifications.models import Notification, ReportNotification, ProgressReportNotification, CompletionReportNotification
from ecs.documents.models import Document
from django.utils.translation import ugettext_lazy as _

_form_info = {}

class FieldInfo(object):
    def __init__(self, number, name, paper_label=None, help_text=None, short_label=None, db_field=True):
        self.number = number
        self.name = name
        self.paper_label = paper_label
        self.help_text = help_text
        self.short_label = short_label
        self._db_field = db_field or None
        
    @property
    def label(self):
        return self.short_label or self.paper_label or None
        
    @property
    def db_field(self):
        if self._db_field is True:
            self._db_field = self.model_info.model._meta.get_field(self.name)
        return self._db_field

class FormInfo(object):
    def __init__(self, model, fields=()):
        self.model = model
        self.fields = {}
        for field in fields:
            field.model_info = self
            self.fields[field.name] = field
        _form_info[model.__name__] = self


FormInfo(Notification, fields=(
    FieldInfo(None, 'submission_forms', _(u'studies')),
    FieldInfo('4.', 'comments', _(u'Results and conclusions')),
))

FormInfo(ReportNotification, fields=(
    FieldInfo('3.1', 'reason_for_not_started', _(u'Has the study started?')),
    FieldInfo('3.2', 'recruited_subjects', _(u'Number of recruited patients / subjects')),
    FieldInfo('3.3', 'finished_subjects', _(u'Number of patients / subjects who completed the study')),
    FieldInfo('3.4', 'aborted_subjects', _(u'Number of study discontinuations')),
    FieldInfo('3.5', 'SAE_count', _(u'Number of SAEs')),
    FieldInfo('3.5', 'SUSAR_count', _(u'Number of SASARs')),
))

FormInfo(CompletionReportNotification, fields=(
    FieldInfo(None, 'study_aborted', None, short_label=_(u'The study was aborted')), # 3.6.2
    FieldInfo(None, 'completion_date', None, short_label=_(u'Date of completion')), # 3.6.2
))

FormInfo(ProgressReportNotification, fields=(
    FieldInfo(None, 'runs_till', None, short_label=_(u'Estimated end date')),
    FieldInfo(None, 'extension_of_vote_requested', _(u'I apply for an extension of the validity of the vote')),
))

FormInfo(Document, fields=(
    FieldInfo(None, 'file', _(u'file')),
    FieldInfo(None, 'original_file_name', _(u'file name')),
    FieldInfo(None, 'version', _(u'version')),
    FieldInfo(None, 'date', _(u'date')),
    FieldInfo(None, 'doctype', _(u'type')),
    FieldInfo(None, 'replaces_document', _(u'replace document'))
))

FormInfo(ForeignParticipatingCenter, fields=(
    FieldInfo(None, 'name', _(u'name')),
    FieldInfo(None, 'investigator_name', _(u'investigator')),
))

FormInfo(Measure, fields=(
    FieldInfo(None, 'category', _(u'study reference')),
    FieldInfo(None, 'type', _(u'type')),
    FieldInfo(None, 'count', _(u'number/dose')),
    FieldInfo(None, 'period', _(u'period')),
    FieldInfo(None, 'total', _(u'total')),
))

FormInfo(NonTestedUsedDrug, fields=(
    FieldInfo(None, 'generic_name', _(u'Generic Name')),
    FieldInfo(None, 'preparation_form', _(u'dosage Form')),
    FieldInfo(None, 'dosage', _(u'dosage')),
))


FormInfo(SubmissionForm, fields=(
    # 1. Allgemeines
    FieldInfo('1.1', 'project_title', _(u'project title'), short_label=_('project title (english)')),
    FieldInfo('1.2', 'protocol_number', _(u'protocol number/-name')),
    FieldInfo('1.3', None, _(u'date of protocol')), #'date_of_protocol'
    FieldInfo('1.2.1', 'eudract_number', _(u'EudraCT-Nr.')),
    FieldInfo('1.3.1', None, _(u'ISRCTN-Nr.')), #'isrctn_number'
    FieldInfo(None, 'external_reviewer_suggestions', None, short_label=_(u'external reviewer suggestions'), help_text=_(u'Not necessary for graduate work or retrospective or non-interventional studies')),
    # 1.5 u'Sponsor / Rechnungsempfänger/in (Kontaktperson in der Buchhaltung)'
    FieldInfo('1.5.1', 'sponsor_name', _(u'sponsor name')),
    FieldInfo('1.5.3', 'sponsor_contact_gender', _(u'sex of contact person')),
    FieldInfo('1.5.3', 'sponsor_contact_title', _(u'title of contact person')),
    FieldInfo('1.5.3', 'sponsor_contact_first_name', _(u'first name of contact person')),
    FieldInfo('1.5.3', 'sponsor_contact_last_name', _(u'last name of contact person')),
    FieldInfo('1.5.2', 'sponsor_address', _(u'address')),
    FieldInfo('1.5.2', 'sponsor_zip_code', None, short_label=_(u'postal code')),
    FieldInfo('1.5.2', 'sponsor_city', None, short_label=_(u'city')),
    FieldInfo('1.5.4', 'sponsor_phone', _(u'telephone')),
    FieldInfo('1.5.5', 'sponsor_fax', _(u'fax')),
    FieldInfo('1.5.6', 'sponsor_email', _(u'e-mail')),
    FieldInfo('1.5.1', 'invoice_name', _(u'name')),
    FieldInfo('1.5.3', 'invoice_contact_gender', _(u'sex of contact person')),
    FieldInfo('1.5.3', 'invoice_contact_title', _(u'title of contact person')),
    FieldInfo('1.5.3', 'invoice_contact_first_name', _(u'first name of contact person')),
    FieldInfo('1.5.3', 'invoice_contact_last_name', _(u'last name of contact person')),
    FieldInfo('1.5.2', 'invoice_address', _(u'address')),
    FieldInfo('1.5.2', 'invoice_zip_code', None, short_label=_(u'postal code')),
    FieldInfo('1.5.2', 'invoice_city', None, short_label=_(u'city')),
    FieldInfo('1.5.4', 'invoice_phone', _(u'telephone')),
    FieldInfo('1.5.5', 'invoice_fax', _(u'fax')),
    FieldInfo('1.5.6', 'invoice_email', _(u'e-mail')),
    FieldInfo('1.5.7', 'invoice_uid', _(u'UID-Nummer')),
    FieldInfo(None, 'invoice_uid_verified_level1', None, short_label=_(u'VAT Nr verified (level1)')),
    FieldInfo(None, 'invoice_uid_verified_level2', None, short_label=_(u'VAT Nr verified (level2)')),
    # 2. Eckdaten der Studie
    # 2.1 Art des Projektes
    FieldInfo('2.1.1', 'project_type_non_reg_drug', _(u'Clinical trial of an unregistered drug')),
    FieldInfo('2.1.2', 'project_type_reg_drug', _(u'Clinical testing of a registered product')),
    FieldInfo('2.1.2.1', 'project_type_reg_drug_within_indication', _(u'according to the indication')),
    FieldInfo('2.1.2.2', 'project_type_reg_drug_not_within_indication', _(u'not according to the indication')),
    FieldInfo('2.1.3', 'project_type_medical_method', _(u'Clinical testing of a new medical method')),
    FieldInfo('2.1.4', 'project_type_medical_device', _(u'Clinical investigation of medical devices')),
    FieldInfo('2.1.4.1', 'project_type_medical_device_with_ce', _(u'with CE-marking')),
    FieldInfo('2.1.4.2', 'project_type_medical_device_without_ce', _(u'without CE-marking')),
    FieldInfo('2.1.4.3', 'project_type_medical_device_performance_evaluation', _(u'Performance evaluation (in-vitro diagnostics)')),
    FieldInfo('2.1.5', 'project_type_basic_research', _(u'Non-therapeutic biomedical research involving human subjects (basic research)')),
    FieldInfo('2.1.6', 'project_type_genetic_study', _(u'Genetic survey')),
    FieldInfo('2.1.7', 'project_type_misc', _(u'Other, please specify'), help_text=_(u'e.g. Dietetics, epidemiology, etc.')),
    FieldInfo('2.1.8/9', 'project_type_education_context', _(u'Dissertation / Thesis')),
    FieldInfo('2.1.10', 'project_type_register', _(u'Register')), # new
    FieldInfo('2.1.11', 'project_type_biobank', _(u'Biobank')), # new
    FieldInfo('2.1.12', 'project_type_retrospective', _(u'Retrospective data analysis')), # new
    FieldInfo('2.1.13', 'project_type_questionnaire', _(u'Questionnaire investigation')), # new
    FieldInfo('2.1.14', 'project_type_psychological_study', None, short_label=_(u'Psychological study')), # new
    FieldInfo('2.1.15', 'project_type_nursing_study', _(u'Nursing Scientific Study')), # new
    FieldInfo('2.2', 'specialism', _(u'special field')),
    # 2.3 Arzneimittelstudie (wenn zutreffend)
    FieldInfo('2.3.1', 'pharma_checked_substance', _(u'Test substances')),
    FieldInfo('2.3.2', 'pharma_reference_substance', _(u'Reference substance')),
    # 2.4 Medizinproduktestudie (wenn zutreffend)
    FieldInfo('2.4.1', 'medtech_checked_product', _(u'Test products(e)')),
    FieldInfo('2.4.2', 'medtech_reference_substance', _(u'reference product')),
    FieldInfo('2.5', 'clinical_phase', _(u'Clinical Phase'), help_text=_(u'necessarily indicate, in case of medical devices the most appropriate phase')),
    FieldInfo('2.8', 'already_voted', _(u'There are already votes of other ethics commissions.'), help_text=_(u'If so, upload the votes on the documents tab')),
    FieldInfo('2.9', 'subject_count', _(u'Planned number of trial participants total'), help_text=_(u'all participating centers')),
    # 2.10 Charakterisierung der Prüfungsteilnehmer/innen
    FieldInfo('2.10.1', 'subject_minage', _(u'minimum age')),
    FieldInfo('2.10.2', 'subject_maxage', _(u'maximum age')),
    FieldInfo('2.10.3', 'subject_noncompetents', _(u'Study includes non competent participants')),
    FieldInfo('2.10.4', 'subject_males', _(u'Study includes male participants')),
    FieldInfo('2.10.4', 'subject_females', _(u'Study includes female participants')),
    FieldInfo('2.10.5', 'subject_childbearing', _(u'Study includes women of childbearing age')),
    FieldInfo('2.11', 'subject_duration', _(u'Duration of participation of the individual test participants in the study')),
    FieldInfo('2.11.1', 'subject_duration_active', _(u'active phase')),
    FieldInfo('2.11.2', 'subject_duration_controls', _(u'Follow-up inspections')),
    FieldInfo('2.12', 'subject_planned_total_duration', _(u'Expected total duration of the study')),
    # 3a. Betrifft nur Studien gemäß AMG: Angaben zur Prüfsubstanz (falls nicht in Österreich registriert)
    FieldInfo('3.1', 'substance_registered_in_countries', _(u'Registration in other states?')),
    FieldInfo('3.2', 'substance_preexisting_clinical_tries', _(u'Are there already results of clinical trials for the tested drug?')),
    FieldInfo('3.2.1', 'substance_p_c_t_countries', _(u'3.2.1 Countries in which the tests were conducted')),
    FieldInfo('3.2.2', 'substance_p_c_t_phase', _(u'Phase'), help_text=_(u'If studies are cited in several phases, indicate the highest stage.')),
    FieldInfo('3.2.3', 'substance_p_c_t_period', _(u'period')),
    FieldInfo('3.2.4', 'substance_p_c_t_application_type', _(u'application type(s)')),
    FieldInfo('3.2.5', 'substance_p_c_t_gcp_rules', _(u'Were the clinical tests made according to GCP guidelines')),
    FieldInfo('3.2.6', 'substance_p_c_t_final_report', _(u'Does a final report exist?'), help_text=_(u"If yes, upload the investigator's brochure, relevant data or a report of the Pharmaceutical Advisory Council using the upload tab")),
    FieldInfo(None, 'submission_type', _(u'Submit as')),
    # 4. Betrifft nur Studien gemäß MPG: Angaben zum Medizinprodukt
    FieldInfo('4.1', 'medtech_product_name', _(u'Name of the product')),
    FieldInfo('4.2', 'medtech_manufacturer', _(u'Manufacturer')),
    FieldInfo('4.3', 'medtech_certified_for_exact_indications', _(u'Certified for this indication')),
    FieldInfo('4.4', 'medtech_certified_for_other_indications', _(u'Certified, but for another indication')),
    FieldInfo('4.5', 'medtech_ce_symbol', _(u'The medical product carries a CE mark')),
    FieldInfo('4.6', 'medtech_manual_included', _(u'The product brochure is included.')),
    FieldInfo('4.7', 'medtech_technical_safety_regulations', _(u'What rules or standards have been used for the construction and testing of the medical product (technical safety)')),
    FieldInfo('4.8', 'medtech_departure_from_regulations', _(u'Any deviations from the above provisions (standards)')),
    # 5. Angaben zur Versicherung (gemäß §32 Abs.1 Z.11 und Z.12 und Abs.2 AMG; §§47 und 48 MPG)
    # Diese Angaben müssen in der Patienten- / Probandeninformation enthalten sein!
    FieldInfo('5.1.1', 'insurance_name', _(u'insurance company')),
    FieldInfo('5.1.2', 'insurance_address', _(u'address')),
    FieldInfo('5.1.3', 'insurance_phone', _(u'phone')),
    FieldInfo('5.1.4', 'insurance_contract_number', _(u'policy number')),
    FieldInfo('5.1.5', 'insurance_validity', _(u'validity')),
    # 6. Angaben zur durchzuführenden Therapie und Diagnostik
    FieldInfo('6.3', 'additional_therapy_info', _(u'Additional information on study-related activities and any necessary deviations from the routine treatment')),
    # 7. Strukturierte Kurzfassung des Projektes (in deutscher Sprache, kein Verweis auf das Protokoll)
    FieldInfo('7.1', 'german_project_title', _(u'If original project title is not in German: German translation of the title'), short_label=_(u'project title (kraut-speak)')),
    FieldInfo('7.2', 'german_summary', _(u'project summary'), help_text=_(u'Justification, relevance, design, measures and procedure')),
    FieldInfo('7.3', 'german_preclinical_results', _(u'Results of pre-clinical tests or justification for the waiving of pre-clinical tests')),
    FieldInfo('7.4', 'german_primary_hypothesis', _(u'Primary hypothesis of the study'), help_text=_(u'if relevant, secondary hypotheses')),
    FieldInfo('7.5', 'german_inclusion_exclusion_crit', _(u'Relevant in- and exclusion criteria')),
    FieldInfo('7.6', 'german_ethical_info', _(u'ethical considerations'), help_text=_(u'Identify and describe all possible problems. Describe the possible gain in knowledge that is to be achieved through the study and its significance, and possible risks of harm or burdens to the test participants. Add your own assessment of the benefit / risk ratio.')),
    FieldInfo('7.7', 'german_protected_subjects_info', _(u'Justification for the inclusion of persons from protected groups'), help_text=_(u'e.g. Minor, temporary or permanent non-competent person, if applicable')),
    FieldInfo('7.8', 'german_recruitment_info', _(u'Description of the recruitment process'), help_text=_(u'All material to be used, for example Listings including layout must be enclosed')),
    FieldInfo('7.9', 'german_consent_info', _(u'Approach at test center(s), for informing and  obtaining an informed consent of candidates, or parents or legal representatives, if applicable'), help_text=_(u'who will inform and when, need for legal representation, witnesses, etc.')),
    FieldInfo('7.10', 'german_risks_info', _(u'Risk assessment, foreseeable risks of treatment and procedures to be used'), help_text=_(u'including pain, discomfort, invasion of personal integrity and measures to prevent and / or supply of unexpected / undesirable events')),
    FieldInfo('7.11', 'german_benefits_info', _(u'Expected benefits for the included test participants')),
    FieldInfo('7.12', 'german_relationship_info', _(u'Relation between subject and investigator'), help_text=_(u'e.g. Patient - doctor, student - teacher, employee - employer, etc.')),
    FieldInfo('7.13', 'german_concurrent_study_info', _(u'Procedures on the site, to determine whether a person at a time to be included in another study, participate or whether a required period of time has elapsed since a participation in another study'), help_text=_(u'Of particular importance when healthy volunteers are included in pharmacological studies.')),
    FieldInfo('7.14', 'german_sideeffects_info', _(u'Methods to identify, record, and report undesirable effects'), help_text=_(u'Describe when, by whom and how, for example "free" interviews and/or interviews using lists')),
    FieldInfo('7.15', 'german_statistical_info', _(u'Statistical considerations and reasons for the number of people who should be included in the study'), help_text=_(u'additional information on section 8, if necessary')),
    FieldInfo('7.16', 'german_dataprotection_info', _(u'Methods used to protect the confidentiality of the data collected, the source documents and the samples'), help_text=_(u'additional information on section 8, if necessary')),
    FieldInfo('7.17', 'german_aftercare_info', _(u'Plan for treatment or care after the person has completed their participation in the study'), help_text=_(u'who will be responsible and where')),
    FieldInfo('7.18', 'german_payment_info', _(u'Amount and method of compensation or remuneration to the test participants'), help_text=_(u'Description of the amount to be paid during the exam take and what, for example, Travel expenses, lost income, pain and discomfort, etc.')),
    FieldInfo('7.19', 'german_abort_info', _(u'Rules for the suspension or premature termination of the study at the test center, at the Member State or the entire study')),
    FieldInfo('7.20', 'german_dataaccess_info', _(u'Agreement on access of the examiner(s) to data, publication guidelines, etc'), help_text=_(u'if not included in the protocol')),
    FieldInfo('7.21', 'german_financing_info', _(u'Financing of the study and information on financial or other interests of the examiner'), help_text=_(u'if not included in the protocol')),
    FieldInfo('7.22', 'german_additional_info', _(u'additional information'), help_text=_(u'if necessary')),
    # 8. Biometrie, Datenschutz
    # 8.1 Studiendesign (z.B. doppelblind, randomisiert, kontrolliert, Placebo, Parallelgruppen, multizentrisch)
    FieldInfo(None, 'study_plan_blind', None, short_label=_(u'open / blind / double-blind')),
    FieldInfo('8.1.1', 'study_plan_open', _(u'open'), db_field=False), 
    FieldInfo('8.1.2', 'study_plan_randomized', _(u'randomized')),
    FieldInfo('8.1.3', 'study_plan_parallelgroups', _(u'parallel groups')),
    FieldInfo('8.1.4', 'monocentric', _(u'monocentric'), db_field=False), 
    FieldInfo('8.1.5', 'study_plan_single_blind', _(u'blind'), db_field=False), 
    FieldInfo('8.1.6', 'study_plan_controlled', _(u'controlled')),
    FieldInfo('8.1.7', 'study_plan_cross_over', _(u'cross-over')),
    FieldInfo('8.1.8', 'multicentric', _(u'multicentric'), db_field=False), 
    FieldInfo('8.1.9', 'study_plan_double_blind', _(u'double-blind'), db_field=False), 
    FieldInfo('8.1.10', 'study_plan_placebo', _(u'placebo')),
    FieldInfo('8.1.11', 'study_plan_factorized', _(u'factorized')),
    FieldInfo('8.1.12', 'study_plan_pilot_project', _(u'pilot project')),
    FieldInfo('8.1.13', 'study_plan_observer_blinded', _(u'observer-blinded')),
    FieldInfo('8.1.14', 'study_plan_equivalence_testing', _(u'equivalence testing')),
    FieldInfo('8.1.15', 'study_plan_misc', _(u'misc')),
    FieldInfo('8.1.16', 'study_plan_number_of_groups', _(u'number of groups')),
    FieldInfo('8.1.17', 'study_plan_stratification', _(u'stratification')),
    FieldInfo('8.1.18', 'study_plan_sample_frequency', _(u'sample frequency')),
    FieldInfo('8.1.19', 'study_plan_primary_objectives', _(u'primary objectives')),
    FieldInfo('8.1.20', 'study_plan_null_hypothesis', _(u'null hypothesis')),
    FieldInfo('8.1.21', 'study_plan_alternative_hypothesis', _(u'alternative hypothesis')),
    FieldInfo('8.1.22', 'study_plan_secondary_objectives', _(u'secondary objectives')),
    # 8.2 Studienplanung
    # Die Fallzahlberechnung basiert auf (Alpha = Fehler 1. Art, Power = 1 – Beta = 1 – Fehler 2. Art):
    FieldInfo('8.2.1', 'study_plan_alpha', _(u'Alpha'), help_text=_(u'first order error')),
    FieldInfo('8.2.2', 'study_plan_power', _(u'Power'), help_text=_(u'1 - Beta = 1 - second order error')),
    FieldInfo('8.2.3', 'study_plan_statalgorithm', _(u'statistical algorithm')),
    FieldInfo('8.2.4', 'study_plan_multiple_test', _(u'multiple testing')),
    FieldInfo('8.2.4', 'study_plan_multiple_test_correction_algorithm', _(u'correctionalgorithm')),
    FieldInfo('8.2.5', 'study_plan_dropout_ratio', _(u'Expected number of study dropouts(Drop-out-Quota)')),
    # 8.3 Geplante statistische Analyse
    FieldInfo('8.3.1', 'study_plan_population_intention_to_treat', _(u'Intention-to-treat')),
    FieldInfo('8.3.2', 'study_plan_population_per_protocol', _(u'Per Protocol')),
    FieldInfo('8.3.3', 'study_plan_interim_evaluation', _(u'Interim evaluation')),
    FieldInfo('8.3.3', 'study_plan_abort_crit', _(u'Termination criteria')),
    FieldInfo('8.3.4', 'study_plan_planned_statalgorithm', _(u'Planned use of statistical methods')),
    # 8.4 Dokumentationsbögen / Datenmanagement
    FieldInfo('8.4.1', 'study_plan_dataquality_checking', _(u'Information on the data quality audit')),
    FieldInfo('8.4.2', 'study_plan_datamanagement', _(u'Information on data management')),
    # 8.5 Verantwortliche und Qualifikation
    FieldInfo('8.5.1', 'study_plan_biometric_planning', _(u'Who did the biometric planning (if applicable, proof of qualification)?')),
    FieldInfo('8.5.2', 'study_plan_statistics_implementation', _(u'Who will conduct the statistical analysis (if applicable, proof of qualification)?')),
    # 8.6 Datenschutz
    FieldInfo('8.6.1', 'study_plan_dataprotection_choice', _(u'Information privacy')),
    FieldInfo('8.6.2', 'study_plan_dataprotection_reason', _(u'Justification')),
    FieldInfo('8.6.2', 'study_plan_dataprotection_dvr', _(u'DPR-Nr.')),
    FieldInfo('8.6.3', 'study_plan_dataprotection_anonalgoritm', _(u'How is the anonymization done?')),
    # Name und Unterschrift der Antragstellerin/des Antragstellers
    FieldInfo('9.1', 'submitter_contact_gender', None, short_label=_(u'salutation')),
    FieldInfo('9.1', 'submitter_contact_title', None, short_label=_(u'title')),
    FieldInfo('9.1', 'submitter_contact_first_name', None, short_label=_(u'first name')),
    FieldInfo('9.1', 'submitter_contact_last_name', None, short_label=_(u'last name')),
    FieldInfo(None, 'submitter_email', None, short_label=_(u'e-mail')),

    FieldInfo('9.2', 'submitter_organisation', _(u'Institution / Company')),
    FieldInfo('9.3', 'submitter_jobtitle', _(u'position')),
    # 9.4 Antragsteller/in ist (nur AMG-Studien)
    FieldInfo('9.4.1', 'submitter_is_coordinator', _(u'coordinating examiner (multicentric study)')),
    FieldInfo('9.4.2', 'submitter_is_main_investigator', _(u'Principal investigator (monocentric study)')),
    FieldInfo('9.4.3', 'submitter_is_sponsor', _(u'sponsor / representative of the sponsor')),
    FieldInfo('9.4.4', 'submitter_is_authorized_by_sponsor', _(u'person/organization authorized by the sponsor')),
    FieldInfo(None, 'sponsor_agrees_to_publishing', None, short_label=_(u'The sponsor agrees with the publication.')),
    FieldInfo(None, 'sponsor_agrees_to_publishing', None, short_label=_(u'The sponsor agrees with the publication of following data by the Ethics Commission as appropiate: EC-Number, Submission Date, Project Title, Main Investigator, Sponsor/CRO and the Centres')),
))


FormInfo(Investigator, fields=(
    FieldInfo('10.2', 'organisation', _(u'study site')),
    FieldInfo('', 'ethics_commission', _(u'ethics commission')),
    FieldInfo('', 'main', _(u'principal investigator')),
    FieldInfo('10.1', 'contact_gender', None, short_label=_(u'salutation of the Investigator')),
    FieldInfo('10.1', 'contact_title', None, short_label=_(u'title of the Investigator')),
    FieldInfo('10.1', 'contact_first_name', None, short_label=_(u'first name of the Investigator')),
    FieldInfo('10.1', 'contact_last_name', None, short_label=_(u'last name of the Investigator')),
    FieldInfo('10.3', 'phone', _(u'phone')),
    FieldInfo('10.4', 'mobile', _(u'mobile')),
    FieldInfo('10.5', 'fax', _(u'FAX')),
    FieldInfo('10.6', 'email', _(u'e-mail')),
    FieldInfo('10.7', 'jus_practicandi', _(u'Jus practicandi')),
    FieldInfo('10.8', 'specialist', _(u'specialist for')),
    FieldInfo('10.9', 'certified', _(u'certified')),
    #FieldInfo('10.10', '', u'Präklinische Qualifikation'),  # TODO one is missing, this one or 10.9
    FieldInfo('11.', 'subject_count', _(u'number of participants')),
))

FormInfo(InvestigatorEmployee, fields=(
    FieldInfo(None, 'sex', _(u'Ms/Mr')),
    FieldInfo(None, 'title', _(u'title')),
    FieldInfo(None, 'surname', _(u'first name')),
    FieldInfo(None, 'firstname', _(u'last name')),
    FieldInfo(None, 'organisation', _(u'Institution')),
))

FormInfo(Submission, fields=(
    FieldInfo(None, 'remission', _(u'exemption of fees')),
))

def get_field_info_for_model(model):
    fields = {}
    for cls in reversed(model.mro()):
        if cls.__name__ in _form_info:
            fields.update(_form_info[cls.__name__].fields)
    return sorted(fields.values(), key=lambda f: f.number)

def get_field_info(model=None, name=None, default=None):
    for cls in model.mro():
        if cls.__name__ in _form_info:
            fields = _form_info[cls.__name__].fields
            if name in fields:
                return fields[name]
    return default
    
