# -*- coding: utf-8 -*-
from django.utils.functional import memoize

from ecs.core.models import SubmissionForm, ForeignParticipatingCenter, Measure, NonTestedUsedDrug, Document, Investigator, InvestigatorEmployee
from ecs.core.models import Notification, ReportNotification, ProgressReportNotification, CompletionReportNotification

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
    FieldInfo(None, 'submission_forms', u'Studien'),
    FieldInfo('4.', 'comments', u'Ergebnisse und Schlussfolgerungen'),
))

FormInfo(ReportNotification, fields=(
    FieldInfo('3.1', 'reason_for_not_started', u'Wurde die Studie begonnen?'),
    FieldInfo('3.2', 'recruited_subjects', u'Zahl der rekrutierten Patient/inn/en / Proband/inn/en'),
    FieldInfo('3.3', 'finished_subjects', u'Zahl der Patient/inn/en / Proband/inn/en, die die Studie beendet haben'),
    FieldInfo('3.4', 'aborted_subjects', u'Zahl der Studienabbrüche'),
    FieldInfo('3.5', 'SAE_count', u'Zahl der SAEs'),
    FieldInfo('3.5', 'SUSAR_count', u'Zahl der SASARs'),
))

FormInfo(CompletionReportNotification, fields=(
    FieldInfo(None, 'study_aborted', None, short_label=u'Die Studie wurde abgebrochen'), # 3.6.2
    FieldInfo(None, 'completion_date', None, short_label=u'Datum der Beendigung'), # 3.6.2
))

FormInfo(ProgressReportNotification, fields=(
    FieldInfo(None, 'runs_till', None, short_label=u'Voraussichtliches Enddatum'),
    FieldInfo(None, 'extension_of_vote_requested', u'Ich beantrage die Verlängerung der Gültigkeit des Votums.'),
))

FormInfo(Document, fields=(
    FieldInfo(None, 'file', u'Datei'),
    FieldInfo(None, 'original_file_name', u'Dateiname'),
    FieldInfo(None, 'version', u'Version'),
    FieldInfo(None, 'date', u'Datum'),
    FieldInfo(None, 'doctype', u'Typ'),
))

FormInfo(ForeignParticipatingCenter, fields=(
    FieldInfo(None, 'name', u'Name'),
    FieldInfo(None, 'investigator_name', u'Prüfarzt'),
))

FormInfo(Measure, fields=(
    FieldInfo(None, 'category', u'Studienbezug'),
    FieldInfo(None, 'type', u'Art'),
    FieldInfo(None, 'count', u'Anzahl/Dosis'),
    FieldInfo(None, 'period', u'Zeitraum'),
    FieldInfo(None, 'total', u'Insgesamt'),
))

FormInfo(NonTestedUsedDrug, fields=(
    FieldInfo(None, 'generic_name', u'Generic Name'),
    FieldInfo(None, 'preparation_form', u'Darreichungsform'),
    FieldInfo(None, 'dosage', u'Dosis'),
))


FormInfo(SubmissionForm, fields=(
    # 1. Allgemeines
    FieldInfo('1.1', 'project_title', u'Projekttitel', short_label='Projekttitel (englisch)'),
    FieldInfo('1.2', None, u'Protokollnummer/-bezeichnung'), #'protocol_number'
    FieldInfo('1.3', None, u'Datum des Protokolls'), #'date_of_protocol'
    FieldInfo('1.2.1', 'eudract_number', u'EudraCT-Nr.'),
    FieldInfo('1.3.1', None, u'ISRCTN-Nr.'), #'isrctn_number'
    # 1.5 u'Sponsor / Rechnungsempfänger/in (Kontaktperson in der Buchhaltung)'
    FieldInfo('1.5.1', 'sponsor_name', u'Name'),
    FieldInfo('1.5.3', 'sponsor_contactname', u'Kontaktperson'),
    FieldInfo('1.5.2', 'sponsor_address1', u'Adresse', short_label='Adresse 1'),
    FieldInfo('1.5.2', 'sponsor_address2', None, short_label='Adresse 2'),
    FieldInfo('1.5.2', 'sponsor_zip_code', None, short_label='Postleitzahl'),
    FieldInfo('1.5.2', 'sponsor_city', None, short_label='Stadt'),
    FieldInfo('1.5.4', 'sponsor_phone', u'Telefon'),
    FieldInfo('1.5.5', 'sponsor_fax', u'FAX'),
    FieldInfo('1.5.6', 'sponsor_email', u'e-mail'),
    FieldInfo('1.5.1', 'invoice_name', u'Name'),
    FieldInfo('1.5.3', 'invoice_contactname', u'Kontaktperson'),
    FieldInfo('1.5.2', 'invoice_address1', u'Adresse', short_label='Adresse 1'),
    FieldInfo('1.5.2', 'invoice_address2', None, short_label='Adresse 2'),
    FieldInfo('1.5.2', 'invoice_zip_code', None, short_label='Postleitzahl'),
    FieldInfo('1.5.2', 'invoice_city', None, short_label='Stadt'),
    FieldInfo('1.5.4', 'invoice_phone', u'Telefon'),
    FieldInfo('1.5.5', 'invoice_fax', u'FAX'),
    FieldInfo('1.5.6', 'invoice_email', u'e-mail'),
    FieldInfo('1.5.7', 'invoice_uid', u'UID-Nummer'),
    FieldInfo(None, 'invoice_uid_verified_level1', None, short_label=u'MWST Nr verifiziert (Stufe1)'),
    FieldInfo(None, 'invoice_uid_verified_level2', None, short_label=u'MWST Nr verifiziert (Stufe2)'),
    # 2. Eckdaten der Studie
    # 2.1 Art des Projektes
    FieldInfo('2.1.1', 'project_type_non_reg_drug', u'Klinische Prüfung eines nicht registrierten Arzneimittels'),
    FieldInfo('2.1.2', 'project_type_reg_drug', u'Klinische Prüfung eines registrierten Arzneimittels'),
    FieldInfo('2.1.2.1', 'project_type_reg_drug_within_indication', u'gemäß der Indikation'),
    FieldInfo('2.1.2.2', 'project_type_reg_drug_not_within_indication', u'nicht gemäß der Indikation'),
    FieldInfo('2.1.3', 'project_type_medical_method', u'Klinische Prüfung einer neuen medizinischen Methode'),
    FieldInfo('2.1.4', 'project_type_medical_device', u'Klinische Prüfung eines Medizinproduktes'),
    FieldInfo('2.1.4.1', 'project_type_medical_device_with_ce', u'mit CE-Kennzeichnung'),
    FieldInfo('2.1.4.2', 'project_type_medical_device_without_ce', u'ohne CE-Kennzeichnung'),
    FieldInfo('2.1.4.3', 'project_type_medical_device_performance_evaluation', u'Leistungsbewertungsprüfung (In-vitro-Diagnostika)'),
    FieldInfo('2.1.5', 'project_type_basic_research', u'Nicht-therapeutische biomedizinische Forschung am Menschen (Grundlagenforschung)'),
    FieldInfo('2.1.6', 'project_type_genetic_study', u'Genetische Untersuchung'),
    FieldInfo('2.1.7', 'project_type_register', u'Register'), # new
    FieldInfo('2.1.8', 'project_type_biobank', u'Biobank'), # new
    FieldInfo('2.1.9', 'project_type_retrospective', u'Retrospektive Datenauswertung'), # new
    FieldInfo('2.1.10', 'project_type_questionnaire', u'Fragebogen Untersuchung'), # new
    FieldInfo('2.1.11', 'project_type_misc', u'Sonstiges, bitte spezifizieren', help_text=u'z.B. Diätetik, Epidemiologie, etc.'), # was: 2.17
    FieldInfo('2.1.12', 'project_type_education_context', u'Dissertation / Diplomarbeit'), # was: 2.1.8 + 2.1.9
    FieldInfo('2.2', 'specialism', u'Fachgebiet'),
    # 2.3 Arzneimittelstudie (wenn zutreffend)
    FieldInfo('2.3.1', 'pharma_checked_substance', u'Prüfsubstanz(en)'),
    FieldInfo('2.3.2', 'pharma_reference_substance', u'Referenzsubstanz'),
    # 2.4 Medizinproduktestudie (wenn zutreffend)
    FieldInfo('2.4.1', 'medtech_checked_product', u'Prüfprodukt(e)'),
    FieldInfo('2.4.2', 'medtech_reference_substance', u'Referenzprodukt'),
    FieldInfo('2.5', 'clinical_phase', u'Klinische Phase', help_text=u'unbedingt angeben, bei Medizinprodukten die am ehesten zutreffende Phase'),
    FieldInfo('2.8', 'already_voted', u'Liegen bereits Voten anderer Ethikkommissionen vor?', help_text=u'Wenn ja, Voten beilegen!'),
    FieldInfo('2.9', 'subject_count', u'Geplante Anzahl der Prüfungsteilnehmer/innen gesamt', help_text=u'alle teilnehmenden Zentren'),
    # 2.10 Charakterisierung der Prüfungsteilnehmer/innen
    FieldInfo('2.10.1', 'subject_minage', u'Mindestalter'),
    FieldInfo('2.10.2', 'subject_maxage', u'Höchstalter'),
    FieldInfo('2.10.3', 'subject_noncompetents', u'Sind auch nicht persönlich Einwilligungsfähige einschließbar?'),
    FieldInfo('2.10.4', 'subject_males', u'männliche'),
    FieldInfo('2.10.4', 'subject_females', u'weibliche'),
    FieldInfo('2.10.5', 'subject_childbearing', u'Sind gebärfähige Frauen einschließbar?'),
    FieldInfo('2.11', 'subject_duration', u'Dauer der Teilnahme der einzelnen Prüfungsteilnehmer/innen an der Studie'),
    FieldInfo('2.11.1', 'subject_duration_active', u'Aktive Phase'),
    FieldInfo('2.11.2', 'subject_duration_controls', u'Nachkontrollen'),
    FieldInfo('2.12', 'subject_planned_total_duration', u'Voraussichtliche Gesamtdauer der Studie'),
    # 3a. Betrifft nur Studien gemäß AMG: Angaben zur Prüfsubstanz (falls nicht in Österreich registriert)
    FieldInfo('3.1', 'substance_registered_in_countries', u'Registrierung in anderen Staaten?'),
    FieldInfo('3.2', 'substance_preexisting_clinical_tries', u'Liegen über das zu prüfende Arzneimittel bereits aussagekräftige Ergebnisse von klinischen Prüfungen vor?'),
    FieldInfo('3.2.1', 'substance_p_c_t_countries', u'3.2.1 In welchen Staaten wurden die Prüfungen durchgeführt?'),
    FieldInfo('3.2.2', 'substance_p_c_t_phase', u'Phase', help_text=u'Wenn Studien in mehreren Phasen angeführt sind, die höchste Phase angeben'),
    FieldInfo('3.2.3', 'substance_p_c_t_period', u'Zeitraum'),
    FieldInfo('3.2.4', 'substance_p_c_t_application_type', u'Anwendungsart(en)'),
    FieldInfo('3.2.5', 'substance_p_c_t_gcp_rules', u'Wurde(n), die klinische(n) Prüfung(en) gemäß GCP-Richtlinien durchgeführt?'),
    FieldInfo('3.2.6', 'substance_p_c_t_final_report', u'Liegt ein Abschlußbericht vor?', help_text=u'Wenn ja, bitte legen Sie die Investigator´s Brochure, relevante Daten oder ein Gutachten des Arznei­mittelbeirates bei.'),
    # 4. Betrifft nur Studien gemäß MPG: Angaben zum Medizinprodukt
    FieldInfo('4.1', 'medtech_product_name', u'Bezeichnung des Produktes'),
    FieldInfo('4.2', 'medtech_manufacturer', u'Hersteller'),
    FieldInfo('4.3', 'medtech_certified_for_exact_indications', u'Zertifiziert für diese Indikation'),
    FieldInfo('4.4', 'medtech_certified_for_other_indications', u'Zertifiziert, aber für eine andere Indikation'),
    FieldInfo('4.5', 'medtech_ce_symbol', u'Das Medizinprodukt trägt ein CE-Zeichen'),
    FieldInfo('4.6', 'medtech_manual_included', u'Die Produktbroschüre liegt bei.'),
    FieldInfo('4.7', 'medtech_technical_safety_regulations', u'Welche Bestimmungen bzw. Normen sind für die Konstruktion und Prüfung des Medizinproduktes herangezogen worden (Technische Sicherheit)'),
    FieldInfo('4.8', 'medtech_departure_from_regulations', u'Allfällige Abweichungen von den o.a. Bestimmungen (Normen)'),
    # 5. Angaben zur Versicherung (gemäß §32 Abs.1 Z.11 und Z.12 und Abs.2 AMG; §§47 und 48 MPG)
    # Diese Angaben müssen in der Patienten- / Probandeninformation enthalten sein!
    FieldInfo('5.1.1', 'insurance_name', u'Versicherungsgesellschaft'),
    FieldInfo('5.1.2', 'insurance_address_1', u'Adresse'),
    FieldInfo('5.1.3', 'insurance_phone', u'Telefon'),
    FieldInfo('5.1.4', 'insurance_contract_number', u'Polizzennummer'),
    FieldInfo('5.1.5', 'insurance_validity', u'Gültigkeitsdauer'),
    # 6. Angaben zur durchzuführenden Therapie und Diagnostik
    FieldInfo('6.3', 'additional_therapy_info', u'Ergänzende Informationen zu studienbezogenen Maßnahmen und alle erforderlichen Abweichungen von der Routinebehandlung'),
    # 7. Strukturierte Kurzfassung des Projektes (in deutscher Sprache, kein Verweis auf das Protokoll)
    FieldInfo('7.1', 'german_project_title', u'Wenn Original-Projekttitel nicht in Deutsch: Deutsche Übersetzung des Titels', short_label=u'Projekttitel (deutsch)'),
    FieldInfo('7.2', 'german_summary', u'Zusammenfassung des Projektes', help_text=u'Rechtfertigung, Relevanz, Design, Maßnahmen und Vorgehensweise'),
    FieldInfo('7.3', 'german_preclinical_results', u'Ergebnisse der prä-klinischen Tests oder Begründung für den Verzicht auf prä-klinischen Tests'),
    FieldInfo('7.4', 'german_primary_hypothesis', u'Primäre Hypothese der Studie', help_text=u'wenn relevant auch sekundäre Hypothesen'),
    FieldInfo('7.5', 'german_inclusion_exclusion_crit', u'Relevante Ein- und Ausschlusskriterien'),
    FieldInfo('7.6', 'german_ethical_info', u'Ethische Überlegungen', help_text=u'Identifizieren und beschreiben Sie alle möglicherweise auftretenden Probleme. Beschreiben Sie den mög­lichen Wissenszuwachs, der durch die Studie erzielt werden soll und seine Bedeutung, sowie mögliche Risi­ken für Schädigungen oderBelastungen der Prüfungsteilnehmer/innen. Legen Sie Ihre eigene Bewertung des Nutzen/Risiko-Verhältnisses dar'),
    FieldInfo('7.7', 'german_protected_subjects_info', u'Begründung für den Einschluss von Personen aus geschützten Gruppen', help_text=u'z.B. Minderjährige, temporär oder permanent nicht-einwilligungsfähige Personen; wenn zutreffend'),
    FieldInfo('7.8', 'german_recruitment_info', u'Beschreibung des Rekrutierungsverfahrens', help_text=u'alle zur Verwendung bestimmte Materialien, z.B. Inserate inkl. Layout müssen beigelegt werden'),
    FieldInfo('7.9', 'german_consent_info', u'Vorgehensweise an der/den Prüfstelle(n), zur Information und Erlangung der informierten Einwil­ligung von Prüfungsteilnehmer/inne/n, bzw. Eltern oder gesetzlichen Vertreter/inne/n, wenn zu-treffend', help_text='wer wird informieren und wann, Erfordernis für gesetzliche Vertretung, Zeugen, etc.'),
    FieldInfo('7.10', 'german_risks_info', u'Risikoabschätzung, vorhersehbare Risiken der Behandlung und sonstiger Verfahren, die verwendet werden sollen', help_text=u'inkl. Schmerzen, Unannehmlichkeiten, Verletzung der persönlichen Integrität und Maßnah­men zur Vermeidung und/oder Versorgung von unvorhergesehenen / unerwünschten Ereignissen'),
    FieldInfo('7.11', 'german_benefits_info', u'Voraussichtliche Vorteile für die eingeschlossenen Prüfungsteilnehmer/innen'),
    FieldInfo('7.12', 'german_relationship_info', u'Relation zwischen Prüfungsteilnehmer/in und Prüfer/in', help_text=u'z.B. Patient/in - Ärztin/Arzt, Student/in - Lehrer/in, Dienstnehmer/in - Dienstgeber/in, etc.'),
    FieldInfo('7.13', 'german_concurrent_study_info', u'Verfahren an der/den Prüfstelle(n), zur Feststellung, ob eine einzuschließende Person gleichzeitig an einer anderen Studie teilnimmt oder ob eine erforderliche Zeitspanne seit einer Teilnahme an einer anderen Studie verstrichen ist', help_text=u'von besonderer Bedeutung, wenn gesunde Proband/inn/en in pharmakologische Studien eingeschlossen werden'),
    FieldInfo('7.14', 'german_sideeffects_info', u'Methoden, um unerwünschte Effekte ausfindig zu machen, sie aufzuzeichnen und zu berichten', help_text=u'Beschreiben Sie wann, von wem und wie, z.B. freies Befragen und/oder an Hand von Listen'),
    FieldInfo('7.15', 'german_statistical_info', u'Statistische Überlegungen und Gründe für die Anzahl der Personen, die in die Studie eingeschlossen werden sollen', help_text=u'ergänzende Informationen zu Punkt 8, wenn erforderlich'),
    FieldInfo('7.16', 'german_dataprotection_info', u'Verwendete Verfahren zum Schutz der Vertraulichkeit der erhobenen Daten, der Quell­dokumente und von Proben', help_text=u'ergänzende Informationen zu Punkt 8, wenn erforderlich'),
    FieldInfo('7.17', 'german_aftercare_info', u'Plan zur Behandlung oder Versorgung nachdem die Personen ihre Teilnahme an der Studie beendet haben', help_text=u'wer wird verantwortlich sein und wo'),
    FieldInfo('7.18', 'german_payment_info', u'Betrag und Verfahren der Entschädigung oder Vergütung an die Prüfungsteilnehmer/innen', help_text=u'Beschreibung des Betrages, der während der Prüfungsteilnahme bezahlt wird und wofür, z.B. Fahrtspesen, Einkommensverlust, Schmerzen und Unannehmlichkeiten, etc.'),
    FieldInfo('7.19', 'german_abort_info', u'Regeln für das Aussetzen oder vorzeitige Beenden der Studie an der/den Prüfstelle(n), in diesem Mitgliedstaat oder der gesamten Studie'),
    FieldInfo('7.20', 'german_dataaccess_info', u'Vereinbarung über den Zugriff der Prüferin/des Prüfers/der Prüfer auf Daten, Publikationsricht­linien, etc.', help_text=u'wenn nicht im Protokoll dargestellt'),
    FieldInfo('7.21', 'german_financing_info', u'Finanzierung der Studie und Informationen über finanzielle oder andere Interessen der Prüferin/des Prüfers/der Prüfer', help_text=u'wenn nicht im Protokoll dargestellt'),
    FieldInfo('7.22', 'german_additional_info', u'Weitere Informationen', help_text=u'wenn erforderlich'),
    # 8. Biometrie, Datenschutz
    # 8.1 Studiendesign (z.B. doppelblind, randomisiert, kontrolliert, Placebo, Parallelgruppen, multizentrisch)
    FieldInfo(None, 'study_plan_blind', None, short_label=u'Offen / blind / doppelblind'),
    FieldInfo('8.1.1', 'study_plan_open', u'offen', db_field=False), 
    FieldInfo('8.1.2', 'study_plan_randomized', u'randomisiert'),
    FieldInfo('8.1.3', 'study_plan_parallelgroups', u'Parallelgruppen'),
    FieldInfo('8.1.4', 'monocentric', u'monozentrisch', db_field=False), 
    FieldInfo('8.1.5', 'study_plan_single_blind', u'blind', db_field=False), 
    FieldInfo('8.1.6', 'study_plan_controlled', u'kontrolliert'),
    FieldInfo('8.1.7', 'study_plan_cross_over', u'cross-over'),
    FieldInfo('8.1.8', 'multicentric', u'multizentrisch', db_field=False), 
    FieldInfo('8.1.9', 'study_plan_double_blind', u'doppelblind', db_field=False), 
    FieldInfo('8.1.10', 'study_plan_placebo', u'Placebo'),
    FieldInfo('8.1.11', 'study_plan_factorized', u'faktoriell'),
    FieldInfo('8.1.12', 'study_plan_pilot_project', u'Pilotprojekt'),
    FieldInfo('8.1.13', 'study_plan_observer_blinded', u'observer-blinded'),
    FieldInfo('8.1.14', 'study_plan_equivalence_testing', u'Äquivalenzprüfung'),
    FieldInfo('8.1.15', 'study_plan_misc', u'Sonstiges'),
    FieldInfo('8.1.16', 'study_plan_number_of_groups', u'Anzahl der Gruppen'),
    FieldInfo('8.1.17', 'study_plan_stratification', u'Stratifizierung'),
    FieldInfo('8.1.18', 'study_plan_sample_frequency', u'Messwiederholungen'),
    FieldInfo('8.1.19', 'study_plan_primary_objectives', u'Hauptzielgröße'),
    FieldInfo('8.1.20', 'study_plan_null_hypothesis', u'Nullhypothese(n)'),
    FieldInfo('8.1.21', 'study_plan_alternative_hypothesis', u'Alternativhypothese(n)'),
    FieldInfo('8.1.22', 'study_plan_secondary_objectives', u'Nebenzielgrößen'),
    # 8.2 Studienplanung
    # Die Fallzahlberechnung basiert auf (Alpha = Fehler 1. Art, Power = 1 – Beta = 1 – Fehler 2. Art):
    FieldInfo('8.2.1', 'study_plan_alpha', u'Alpha', help_text=u'Fehler 1. Art'),
    FieldInfo('8.2.2', 'study_plan_power', u'Power', help_text=u'1 - Beta = 1 - Fehler 2. Art'),
    FieldInfo('8.2.3', 'study_plan_statalgorithm', u'Stat.Verfahren'),
    FieldInfo('8.2.4', 'study_plan_multiple_test_correction_algorithm', u'Multiples Testen, Korrekturverfahren'),
    FieldInfo('8.2.5', 'study_plan_dropout_ratio', u'Erwartete Anzahl von Studienabbrecher/inne/n (Drop-out-Quote)'),
    # 8.3 Geplante statistische Analyse
    FieldInfo('8.3.1', 'study_plan_population_intention_to_treat', u'Intention-to-treat'),
    FieldInfo('8.3.2', 'study_plan_population_per_protocol', u'Per Protocol'),
    FieldInfo('8.3.3', 'study_plan_abort_crit', u'Zwischenauswertung, Abbruchkriterien'),
    FieldInfo('8.3.4', 'study_plan_planned_statalgorithm', u'Geplante statistische Verfahren'),
    # 8.4 Dokumentationsbögen / Datenmanagement
    FieldInfo('8.4.1', 'study_plan_dataquality_checking', u'Angaben zur Datenqualitätsprüfung'),
    FieldInfo('8.4.2', 'study_plan_datamanagement', u'Angaben zum Datenmanagement'),
    # 8.5 Verantwortliche und Qualifikation
    FieldInfo('8.5.1', 'study_plan_biometric_planning', u'Wer führte die biometrische Planung durch (ggf. Nachweis der Qualifikation)?'),
    FieldInfo('8.5.2', 'study_plan_statistics_implementation', u'Wer wird die statistische Auswertung durchführen (ggf. Nachweis der Qualifikation)?'),
    # 8.6 Datenschutz
    FieldInfo('8.6.2', 'study_plan_dataprotection_reason', u'Begründung'),
    FieldInfo('8.6.2', 'study_plan_dataprotection_dvr', u'DVR-Nummer'),
    FieldInfo('8.6.3', 'study_plan_dataprotection_anonalgoritm', u'Wie erfolgt die Anonymisierung?'),
    # Name und Unterschrift der Antragstellerin/des Antragstellers
    FieldInfo('9.1', 'submitter_name', u'Name'),
    FieldInfo('9.2', 'submitter_organisation', u'Institution/ Firma'),
    FieldInfo('9.3', 'submitter_jobtitle', u'Position'),
    # 9.4 Antragsteller/in ist (nur AMG-Studien)
    FieldInfo('9.4.1', 'submitter_is_coordinator', u'koordinierende/r Prüfer/in (multizentrische Studie)'),
    FieldInfo('9.4.2', 'submitter_is_main_investigator', u'Hauptprüfer/in (monozentrische Studie)'),
    FieldInfo('9.4.3', 'submitter_is_sponsor', u'Sponsor bzw. Vertreter/in des Sponsors'),
    FieldInfo('9.4.4', 'submitter_is_authorized_by_sponsor', u'vom Sponsor autorisierte Person/Organisation'),
    FieldInfo(None, 'submitter_agrees_to_publishing', None, short_label=u'Einreicher stimmt der Veröffentlichung zu'),
))


FormInfo(Investigator, fields=(
    FieldInfo('10.2', 'organisation', u'Prüfzentrum'),
    FieldInfo('', 'ethics_commission', u'Ethik-Kommission'),
    FieldInfo('', 'main', u'Hauptprüfer'),
    FieldInfo('10.1', 'name', u'Prüfarzt Name'),
    FieldInfo('10.3', 'phone', u'Telefon'),
    FieldInfo('10.4', 'mobile', u'"Pieps"/Mobil'),
    FieldInfo('10.5', 'fax', u'Fax'),
    FieldInfo('10.6', 'email', u'e-mail-Adresse'),
    FieldInfo('10.7', 'jus_practicandi', u''),
    FieldInfo('10.8', 'specialist', u'Facharzt für'),
    FieldInfo('10.9', 'certified', u'Prüfärztekurs'),
    #FieldInfo('10.10', '', u'Präklinische Qualifikation'),  # TODO one is missing, this one or 10.9
    FieldInfo('11.', 'subject_count', u'Anzahl Teilnehmer/innen'),
))

FormInfo(InvestigatorEmployee, fields=(
    FieldInfo(None, 'sex', u'Fr/Hr'),
    FieldInfo(None, 'title', u'Titel'),
    FieldInfo(None, 'surname', u'Vorname'),
    FieldInfo(None, 'firstname', u'Name'),
    FieldInfo(None, 'organisation', u'Institution'),
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
    
