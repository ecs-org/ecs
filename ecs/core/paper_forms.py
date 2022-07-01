from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from ecs.core.models import (
    Submission, SubmissionForm, ParticipatingCenterNonSubject,
    ForeignParticipatingCenter, Measure, NonTestedUsedDrug, Investigator,
    InvestigatorEmployee,
)
from ecs.notifications.models import (
    Notification, ReportNotification, ProgressReportNotification,
    CompletionReportNotification, SafetyNotification, CenterCloseNotification,
)
from ecs.documents.models import Document

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
        self.fields = OrderedDict()
        for field in fields:
            field.model_info = self
            self.fields[field.name] = field
        _form_info[model.__name__] = self


FormInfo(Notification, fields=(
    FieldInfo(None, 'submission_forms', _('studies')),
    FieldInfo('3.', 'comments', _('Statement/Conclusion/Notice')),
))

FormInfo(SafetyNotification, fields=(
    FieldInfo(None, 'safety_type', _('Type')),
))

FormInfo(ReportNotification, fields=(
    FieldInfo('3.1', 'study_started', _('The study has been started'), help_text=_('please add additional details to the field "comments"')),
    FieldInfo(None, 'reason_for_not_started', _('Why hasn\'t the study been started?')),
    FieldInfo('3.2', 'recruited_subjects', _('Number of recruited patients / subjects')),
    FieldInfo('3.3', 'finished_subjects', _('Number of patients / subjects who completed the study')),
    FieldInfo('3.4', 'aborted_subjects', _('Number of study discontinuations')),
    FieldInfo('3.5', 'SAE_count', _('Number of SAEs')),
    FieldInfo('3.5', 'SUSAR_count', _('Number of SUSARs')),
))

FormInfo(CompletionReportNotification, fields=(
    FieldInfo(None, 'study_aborted', None, short_label=_('The study was aborted')), # 3.6.2
    FieldInfo(None, 'completion_date', None, short_label=_('Date of completion')), # 3.6.2
))

FormInfo(ProgressReportNotification, fields=(
    FieldInfo(None, 'runs_till', None, short_label=_('Estimated end date')),
))

FormInfo(CenterCloseNotification, fields=(
    FieldInfo(None, 'investigator', _('Closed center')),
    FieldInfo(None, 'close_date', _('Close date')),
))

FormInfo(Document, fields=(
    FieldInfo(None, 'file', _('PDF-file')),
    FieldInfo(None, 'original_file_name', _('file name')),
    FieldInfo(None, 'version', _('version')),
    FieldInfo(None, 'date', _('date of document creation')),
    FieldInfo(None, 'doctype', _('type')),
    FieldInfo(None, 'replaces_document', _('replace document'))
))

FormInfo(ForeignParticipatingCenter, fields=(
    FieldInfo(None, 'name', _('name')),
    FieldInfo(None, 'investigator_name', _('investigator')),
))

FormInfo(ParticipatingCenterNonSubject, fields=(
    FieldInfo(None, 'name', _('name')),
    FieldInfo(None, 'ethics_commission', _('ethics commission')),
    FieldInfo(None, 'investigator_name', _('investigator')),
))

FormInfo(Measure, fields=(
    FieldInfo(None, 'category', _('study reference')),
    FieldInfo(None, 'type', _('type')),
    FieldInfo(None, 'count', _('number/dose')),
    FieldInfo(None, 'period', _('period')),
    FieldInfo(None, 'total', _('total')),
))

FormInfo(NonTestedUsedDrug, fields=(
    FieldInfo(None, 'generic_name', _('Generic Name')),
    FieldInfo(None, 'preparation_form', _('dosage Form')),
    FieldInfo(None, 'dosage', _('dosage')),
))


FormInfo(SubmissionForm, fields=(
    # 1. Allgemeines
    FieldInfo('1.1', 'project_title', _('project title'), short_label=_('project title (english)')),
    FieldInfo('1.3', None, _('date of protocol')), #'date_of_protocol'
    FieldInfo('1.2.1', 'eudract_number', _('EudraCT-Nr.')),
    FieldInfo('1.3.1', None, _('ISRCTN-Nr.')), #'isrctn_number'
    # 1.5 u'Sponsor / Rechnungsempfänger/in (Kontaktperson in der Buchhaltung)'
    FieldInfo('1.5.1', 'sponsor_name', _('sponsor name')),
    FieldInfo('1.5.3', 'sponsor_contact_gender', _('sex of contact person')),
    FieldInfo('1.5.3', 'sponsor_contact_title', _('title of contact person')),
    FieldInfo('1.5.3', 'sponsor_contact_first_name', _('first name of contact person')),
    FieldInfo('1.5.3', 'sponsor_contact_last_name', _('last name of contact person')),
    FieldInfo('1.5.2', 'sponsor_address', _('address')),
    FieldInfo('1.5.2', 'sponsor_zip_code', None, short_label=_('postal code')),
    FieldInfo('1.5.2', 'sponsor_city', None, short_label=_('city')),
    FieldInfo('1.5.4', 'sponsor_phone', _('telephone')),
    FieldInfo('1.5.5', 'sponsor_fax', _('fax')),
    FieldInfo('1.5.6', 'sponsor_email', _('e-mail')),
    FieldInfo('1.5.7', 'sponsor_uid', _('UID-Number')),
    FieldInfo('1.5.1', 'invoice_name', _('invoice name')),
    FieldInfo('1.5.3', 'invoice_contact_gender', _('sex of contact person')),
    FieldInfo('1.5.3', 'invoice_contact_title', _('title of contact person')),
    FieldInfo('1.5.3', 'invoice_contact_first_name', _('first name of contact person')),
    FieldInfo('1.5.3', 'invoice_contact_last_name', _('last name of contact person')),
    FieldInfo('1.5.2', 'invoice_address', _('address')),
    FieldInfo('1.5.2', 'invoice_zip_code', None, short_label=_('postal code')),
    FieldInfo('1.5.2', 'invoice_city', None, short_label=_('city')),
    FieldInfo('1.5.4', 'invoice_phone', _('telephone')),
    FieldInfo('1.5.5', 'invoice_fax', _('fax')),
    FieldInfo('1.5.6', 'invoice_email', _('e-mail')),
    FieldInfo('1.5.7', 'invoice_uid', _('UID-Number')),
    # 2. Eckdaten der Studie
    # 2.1 Art des Projektes
    FieldInfo('2.1.1', 'project_type_non_reg_drug', _('Clinical trial of an unregistered drug')),
    FieldInfo('2.1.2', 'project_type_reg_drug', _('Clinical testing of a registered product')),
    FieldInfo('2.1.2.1', 'project_type_reg_drug_within_indication', _('according to the indication')),
    FieldInfo('2.1.2.2', 'project_type_reg_drug_not_within_indication', _('not according to the indication')),
    FieldInfo('2.1.3', 'project_type_medical_method', _('Clinical testing of a new medical method')),
    FieldInfo('2.1.4', 'project_type_medical_device', _('Clinical investigation of medical devices')),
    FieldInfo('2.1.4.1', 'project_type_medical_device_with_ce', _('with CE-marking')),
    FieldInfo('2.1.4.2', 'project_type_medical_device_without_ce', _('without CE-marking')),
    FieldInfo('2.1.4.3', 'project_type_medical_device_performance_evaluation', _('Performance evaluation (in-vitro diagnostics)')),
    FieldInfo('2.1.5', 'project_type_basic_research', _('Non-therapeutic biomedical research involving human subjects (basic research)')),
    FieldInfo('2.1.6', 'project_type_genetic_study', _('Genetic survey')),
    FieldInfo('2.1.7', 'project_type_misc', _('Other, please specify'), help_text=_('e.g. Dietetics, epidemiology, etc.')),
    FieldInfo('2.1.8/9', 'project_type_education_context', _('Dissertation / Thesis')),
    FieldInfo('2.1.10', 'project_type_register', _('Register')),
    FieldInfo('2.1.11', 'project_type_biobank', _('Biobank')),
    FieldInfo('2.1.12', 'project_type_retrospective', _('Retrospective data analysis')),
    FieldInfo('2.1.13', 'project_type_questionnaire', _('Questionnaire investigation')),
    FieldInfo('2.1.14', 'project_type_psychological_study', None, short_label=_('Psychological study')),
    FieldInfo('2.1.15', 'project_type_nursing_study', _('Nursing Scientific Study')),
    FieldInfo('2.1.16', 'project_type_non_interventional_study', _('Non-interventional Study (NIS)')),
    FieldInfo('2.1.17', 'project_type_gender_medicine', _('Gender medicine')),
    FieldInfo('2.2', 'specialism', _('special field')),
    # 2.3 Arzneimittelstudie (wenn zutreffend)
    FieldInfo('2.3.1', 'pharma_checked_substance', _('Test substances')),
    FieldInfo('2.3.2', 'pharma_reference_substance', _('Reference substance')),
    # 2.4 Medizinproduktestudie (wenn zutreffend)
    FieldInfo('2.4.1', 'medtech_checked_product', _('Test products(e)')),
    FieldInfo('2.4.2', 'medtech_reference_substance', _('reference product')),
    FieldInfo('2.5', 'clinical_phase', _('Clinical Phase'), help_text=_('Necessarily indicate, in case of an AMG-study the clinical phase, in case of medical devices the most appropriate phase.')),
    FieldInfo('2.8', 'already_voted', _('There are already votes of other ethics commissions.'), help_text=_('If so, upload the votes on the documents tab')),
    FieldInfo('2.9', 'subject_count', _('Planned number of trial participants total'), help_text=_('all participating centers')),
    # 2.10 Charakterisierung der Prüfungsteilnehmer/innen
    FieldInfo('2.10.1', 'subject_minage', _('minimum age')),
    FieldInfo('2.10.2', 'subject_maxage', _('maximum age')),

    FieldInfo('2.10.4', 'subject_males', _('male participants')),
    FieldInfo('2.10.4/5', 'subject_females_childbearing', _('female participants')),
    FieldInfo('2.10.4', 'subject_females', _('female participants')),
    FieldInfo('2.10.5', 'subject_childbearing', _('women of childbearing age')),
    FieldInfo('2.10.3', 'subject_noncompetents', _('non competent participants'), help_text=_('non competents explanation')),

    FieldInfo('2.11', 'subject_duration', _('Duration of participation of the individual test participants in the study')),
    FieldInfo('2.11.1', 'subject_duration_active', _('active phase')),
    FieldInfo('2.11.2', 'subject_duration_controls', _('Follow-up inspections')),
    FieldInfo('2.12', 'subject_planned_total_duration', _('Expected total duration of the study')),
    # 3a. Betrifft nur Studien gemäß AMG: Angaben zur Prüfsubstanz (falls nicht in Österreich registriert)
    FieldInfo(None, 'submission_type', _('Submit as')),
    FieldInfo('3.1', 'substance_registered_in_countries', _('Registration in other states?')),
    FieldInfo('3.2', 'substance_preexisting_clinical_tries', _('Are there already results of clinical trials for the tested drug?')),
    FieldInfo('3.2.1', 'substance_p_c_t_countries', _('3.2.1 Countries in which the tests were conducted')),
    FieldInfo('3.2.2', 'substance_p_c_t_phase', _('Phase'), help_text=_('If studies are cited in several phases, indicate the highest stage.')),
    FieldInfo('3.2.3', 'substance_p_c_t_period', _('period')),
    FieldInfo('3.2.4', 'substance_p_c_t_application_type', _('application type(s)')),
    FieldInfo('3.2.5', 'substance_p_c_t_gcp_rules', _('Were the clinical tests made according to GCP guidelines')),
    FieldInfo('3.2.6', 'substance_p_c_t_final_report', _('Does a final report exist?'), help_text=_("If yes, upload the investigator's brochure, relevant data or a report of the Pharmaceutical Advisory Council using the upload tab")),
    # 4. Betrifft nur Studien gemäß MPG: Angaben zum Medizinprodukt
    FieldInfo(None, 'medtech_is_new_law', _('Is new medtech law')),
    FieldInfo('4.1', 'medtech_product_name', _('Name of the product')),
    FieldInfo('4.2', 'medtech_manufacturer', _('Manufacturer')),
    FieldInfo('4.3', 'medtech_certified_for_exact_indications', _('Certified for this indication')),
    FieldInfo('4.4', 'medtech_certified_for_other_indications', _('Certified, but for another indication')),
    FieldInfo('4.5', 'medtech_ce_symbol', _('The medical product carries a CE mark')),
    FieldInfo('4.6', 'medtech_manual_included', _('The product brochure is included.')),
    FieldInfo('4.7', 'medtech_technical_safety_regulations', _('What rules or standards have been used for the construction and testing of the medical product (technical safety)')),
    FieldInfo('4.8', 'medtech_departure_from_regulations', _('Any deviations from the above provisions (standards)')),
    # 5. Angaben zur Versicherung (gemäß §32 Abs.1 Z.11 und Z.12 und Abs.2 AMG; §§47 und 48 MPG)
    # Diese Angaben müssen in der Patienten- / Probandeninformation enthalten sein!
    FieldInfo(None, 'insurance_not_required', _('No insurance is required')),
    FieldInfo('5.1.1', 'insurance_name', _('insurance company')),
    FieldInfo('5.1.2', 'insurance_address', _('address')),
    FieldInfo('5.1.3', 'insurance_phone', _('phone')),
    FieldInfo('5.1.4', 'insurance_contract_number', _('policy number')),
    FieldInfo('5.1.5', 'insurance_validity', _('validity')),
    # 6. Angaben zur durchzuführenden Therapie und Diagnostik
    FieldInfo('6.3', 'additional_therapy_info', _('Additional information on study-related activities and any necessary deviations from the routine treatment')),
    # 7. Strukturierte Kurzfassung des Projektes (in deutscher Sprache, kein Verweis auf das Protokoll)
    FieldInfo('7.1', 'german_project_title', _('If original project title is not in German: German translation of the title'), short_label=_('project title (kraut-speak)')),
    FieldInfo('7.2', 'german_summary', _('project summary'), help_text=_('Justification, relevance, design, measures and procedure')),
    FieldInfo('7.3', 'german_preclinical_results', _('Results of pre-clinical tests or justification for the waiving of pre-clinical tests')),
    FieldInfo('7.4', 'german_primary_hypothesis', _('Primary hypothesis of the study'), help_text=_('if relevant, secondary hypotheses')),
    FieldInfo('7.5', 'german_inclusion_exclusion_crit', _('Relevant in- and exclusion criteria')),
    FieldInfo('7.6', 'german_ethical_info', _('ethical considerations')),
    FieldInfo('7.7', 'german_protected_subjects_info', _('Justification for the inclusion of persons from protected groups'), help_text=_('e.g. Minor, temporary or permanent non-competent person, if applicable')),
    FieldInfo('7.8', 'german_recruitment_info', _('Description of the recruitment process')),
    FieldInfo('7.9', 'german_consent_info', _('Approach at test center(s), for informing and  obtaining an informed consent of candidates')),
    FieldInfo('7.10', 'german_risks_info', _('Risk assessment')),
    FieldInfo('7.11', 'german_benefits_info', _('Expected benefits for the included test participants')),
    FieldInfo('7.12', 'german_relationship_info', _('Relation between subject and investigator'), help_text=_('e.g. Patient - doctor, student - teacher, employee - employer, etc.')),
    FieldInfo('7.13', 'german_concurrent_study_info', _('Procedures on the site, to determine whether a person at a time to be included in another study, participate or whether a required period of time has elapsed since a participation in another study'), help_text=_('Of particular importance when healthy volunteers are included in pharmacological studies.')),
    FieldInfo('7.14', 'german_sideeffects_info', _('Methods to identify, record, and report undesirable effects'), help_text=_('Describe when, by whom and how, for example "free" interviews and/or interviews using lists')),
    FieldInfo('7.15', 'german_statistical_info', _('Statistical considerations and reasons for the number of people who should be included in the study'), help_text=_('additional information on section 8, if necessary')),
    FieldInfo('7.16', 'german_dataprotection_info', _('Methods used to protect the confidentiality of the data collected, the source documents and the samples'), help_text=_('additional information on section 8, if necessary')),
    FieldInfo('7.17', 'german_aftercare_info', _('Plan for treatment or care after the person has completed their participation in the study')),
    FieldInfo('7.18', 'german_payment_info', _('Amount and method of compensation or remuneration to the test participants'), help_text=_('Description of the amount to be paid during the exam take and what, for example, Travel expenses, lost income, pain and discomfort, etc.')),
    FieldInfo('7.19', 'german_abort_info', _('Rules for the suspension or premature termination of the study at the test center, at the Member State or the entire study')),
    FieldInfo('7.20', 'german_dataaccess_info', _('Agreement on access of the examiner(s) to data, publication guidelines, etc')),
    FieldInfo('7.21', 'german_financing_info', _('Financing of the study and information on financial or other interests of the examiner')),
    FieldInfo('7.22', 'german_additional_info', _('additional information')),
    # 8. Biometrie, Datenschutz
    # 8.1 Studiendesign (z.B. doppelblind, randomisiert, kontrolliert, Placebo, Parallelgruppen, multizentrisch)
    FieldInfo(None, 'study_plan_blind', None, short_label=_('Open / Blind / Double-blind')),
    FieldInfo('8.1.1', 'study_plan_open', _('open'), db_field=False),
    FieldInfo('8.1.2', 'study_plan_randomized', _('randomized')),
    FieldInfo('8.1.3', 'study_plan_parallelgroups', _('parallel groups')),
    FieldInfo('8.1.4', 'is_monocentric', _('monocentric'), db_field=False),
    FieldInfo('8.1.5', 'study_plan_single_blind', _('blind'), db_field=False),
    FieldInfo('8.1.6', 'study_plan_controlled', _('controlled')),
    FieldInfo('8.1.7', 'study_plan_cross_over', _('cross-over')),
    FieldInfo('8.1.8', 'is_multicentric', _('multicentric'), db_field=False),
    FieldInfo('8.1.9', 'study_plan_double_blind', _('double-blind'), db_field=False),
    FieldInfo('8.1.10', 'study_plan_placebo', _('placebo')),
    FieldInfo('8.1.11', 'study_plan_factorized', _('factorized')),
    FieldInfo('8.1.12', 'study_plan_pilot_project', _('pilot project')),
    FieldInfo('8.1.13', 'study_plan_observer_blinded', _('observer-blinded')),
    FieldInfo('8.1.14', 'study_plan_equivalence_testing', _('equivalence testing')),
    FieldInfo('8.1.15', 'study_plan_misc', _('misc')),
    FieldInfo('8.1.16', 'study_plan_number_of_groups', _('number of groups')),
    FieldInfo('8.1.17', 'study_plan_stratification', _('stratification')),
    FieldInfo('8.1.18', 'study_plan_sample_frequency', _('sample frequency')),
    FieldInfo('8.1.19', 'study_plan_primary_objectives', _('primary objectives')),
    FieldInfo('8.1.20', 'study_plan_null_hypothesis', _('null hypothesis')),
    FieldInfo('8.1.21', 'study_plan_alternative_hypothesis', _('alternative hypothesis')),
    FieldInfo('8.1.22', 'study_plan_secondary_objectives', _('secondary objectives')),
    # 8.2 Studienplanung
    # Die Fallzahlberechnung basiert auf (Alpha = Fehler 1. Art, Power = 1 – Beta = 1 – Fehler 2. Art):
    FieldInfo('8.2.1', 'study_plan_alpha', _('Alpha'), help_text=_('first order error')),
    FieldInfo(None, 'study_plan_alpha_sided', ' '),
    FieldInfo('8.2.2', 'study_plan_power', _('Power'), help_text=_('1 - Beta = 1 - second order error')),
    FieldInfo('8.2.3', 'study_plan_statalgorithm', _('statistical algorithm')),
    FieldInfo('8.2.4', 'study_plan_multiple_test', _('multiple testing')),
    FieldInfo('8.2.4', 'study_plan_multiple_test_correction_algorithm', _('correctionalgorithm')),
    FieldInfo('8.2.5', 'study_plan_dropout_ratio', _('Expected number of study dropouts(Drop-out-Quota)')),
    # 8.3 Geplante statistische Analyse
    FieldInfo('8.3.1', 'study_plan_population_intention_to_treat', _('Intention-to-treat')),
    FieldInfo('8.3.2', 'study_plan_population_per_protocol', _('Per Protocol')),
    FieldInfo('8.3.3', 'study_plan_interim_evaluation', _('Interim evaluation')),
    FieldInfo('8.3.3', 'study_plan_abort_crit', _('Termination criteria')),
    FieldInfo('8.3.4', 'study_plan_planned_statalgorithm', _('Planned use of statistical methods')),
    # 8.4 Dokumentationsbögen / Datenmanagement
    FieldInfo('8.4.1', 'study_plan_dataquality_checking', _('Information on the data quality audit')),
    FieldInfo('8.4.2', 'study_plan_datamanagement', _('Information on data management')),
    # 8.5 Verantwortliche und Qualifikation
    FieldInfo('8.5.1', 'study_plan_biometric_planning', _('Who did the biometric planning (if applicable, proof of qualification)?')),
    FieldInfo('8.5.2', 'study_plan_statistics_implementation', _('Who will conduct the statistical analysis (if applicable, proof of qualification)?')),
    # 8.6 Datenschutz
    FieldInfo('8.6.1', 'study_plan_dataprotection_choice', _('Information privacy')),
    FieldInfo('8.6.2', 'study_plan_dataprotection_reason', _('Justification')),
    FieldInfo('8.6.2', 'study_plan_dataprotection_dvr', _('DPR-Nr.')),
    FieldInfo('8.6.3', 'study_plan_dataprotection_anonalgoritm', _('How is the anonymization done?')),
    # Name und Unterschrift der Antragstellerin/des Antragstellers
    FieldInfo('9.1', 'submitter_contact_gender', None, short_label=_('salutation')),
    FieldInfo('9.1', 'submitter_contact_title', None, short_label=_('title')),
    FieldInfo('9.1', 'submitter_contact_first_name', None, short_label=_('first name')),
    FieldInfo('9.1', 'submitter_contact_last_name', None, short_label=_('last name')),
    FieldInfo(None, 'submitter_email', None, short_label=_('e-mail')),

    FieldInfo('9.2', 'submitter_organisation', _('Institution / Company')),
    FieldInfo('9.3', 'submitter_jobtitle', _('position')),
    # 9.4 Antragsteller/in ist (nur AMG-Studien)
    FieldInfo('9.4.1', 'submitter_is_coordinator', _('The submitter is a coordinating examiner (multicentric study)')),
    FieldInfo('9.4.2', 'submitter_is_main_investigator', _('The submitter is a principal investigator (monocentric study)')),
    FieldInfo('9.4.3', 'submitter_is_sponsor', _('The submitter is a sponsor / representative of the sponsor')),
    FieldInfo('9.4.4', 'submitter_is_authorized_by_sponsor', _('The submitter is a person/organization authorized by the sponsor')),
))


FormInfo(Investigator, fields=(
    FieldInfo('10.2', 'organisation', _('study site')),
    FieldInfo('', 'ethics_commission', _('ethics commission')),
    FieldInfo('', 'main', _('principal investigator')),
    FieldInfo('10.1', 'contact_gender', None, short_label=_('salutation of the Investigator')),
    FieldInfo('10.1', 'contact_title', None, short_label=_('title of the Investigator')),
    FieldInfo('10.1', 'contact_first_name', None, short_label=_('first name of the Investigator')),
    FieldInfo('10.1', 'contact_last_name', None, short_label=_('last name of the Investigator')),
    FieldInfo('10.3', 'phone', _('phone')),
    FieldInfo('10.4', 'mobile', _('mobile')),
    FieldInfo('10.5', 'fax', _('FAX')),
    FieldInfo('10.6', 'email', _('e-mail')),
    FieldInfo('10.7', 'jus_practicandi', _('Jus practicandi')),
    FieldInfo('10.8', 'specialist', _('specialist for')),
    FieldInfo('10.9', 'certified', _('certified')),
    #FieldInfo('10.10', '', u'Präklinische Qualifikation'),  # TODO one is missing, this one or 10.9 - see also Bug #4737
    FieldInfo('11.', 'subject_count', _('number of participants')),
))

FormInfo(InvestigatorEmployee, fields=(
    FieldInfo(None, 'sex', _('Ms/Mr')),
    FieldInfo(None, 'title', _('title')),
    FieldInfo(None, 'firstname', _('first name')),
    FieldInfo(None, 'surname', _('last name')),
    FieldInfo(None, 'organisation', _('Institution')),
))

FormInfo(Submission, fields=(
    FieldInfo(None, 'remission', _('remission')),
))

def get_field_info_for_model(model):
    fields = {}
    for cls in reversed(model.mro()):
        if cls.__name__ in _form_info:
            fields.update(_form_info[cls.__name__].fields)
    return sorted(fields.values(), key=lambda f: f.number or '')

def get_field_info(model=None, name=None, default=None):
    for cls in model.mro():
        if cls.__name__ in _form_info:
            fields = _form_info[cls.__name__].fields
            if name in fields:
                return fields[name]
    return default

def get_field_names_for_model(model):
    return [f for f in _form_info[model.__name__].fields.keys() if f is not None]
