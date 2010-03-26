# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Workflow'
        db.create_table('core_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Workflow'])

        # Adding model 'DocumentType'
        db.create_table('core_documenttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('core', ['DocumentType'])

        # Adding model 'Document'
        db.create_table('core_document', (
            ('mimetype', self.gf('django.db.models.fields.CharField')(default='application/pdf', max_length=100)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('uuid_document_revision', self.gf('django.db.models.fields.SlugField')(max_length=32, db_index=True)),
            ('doctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DocumentType'], null=True, blank=True)),
            ('original_file_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('uuid_document', self.gf('django.db.models.fields.SlugField')(max_length=32, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Document'])

        # Adding model 'EthicsCommission'
        db.create_table('core_ethicscommission', (
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('chairperson', self.gf('django.db.models.fields.CharField')(max_length=120, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('contactname', self.gf('django.db.models.fields.CharField')(max_length=120, null=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('core', ['EthicsCommission'])

        # Adding model 'SubmissionForm'
        db.create_table('core_submissionform', (
            ('invoice_uid', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('study_plan_abort_crit', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('medtech_product_name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('study_plan_statistics_implementation', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('sponsor_fax', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('substance_p_c_t_final_report', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('substance_registered_in_countries', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('project_type_basic_research', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('medtech_ce_symbol', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('study_plan_alpha', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('project_type_reg_drug', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_secondary_objectives', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('eudract_number', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('study_plan_dropout_ratio', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('german_protected_subjects_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('project_type_genetic_study', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_blind', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('study_plan_misc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project_type_retrospective', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_preclinical_results', self.gf('django.db.models.fields.TextField')(null=True)),
            ('study_plan_biometric_planning', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('invoice_uid_verified_level2', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('study_plan_placebo', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_jobtitle', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('project_type_medical_device', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_aftercare_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_recruitment_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('study_plan_factorized', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('invoice_uid_verified_level1', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('project_type_medical_device_performance_evaluation', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_dataprotection_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_concurrent_study_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('study_plan_planned_statalgorithm', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forms', to=orm['core.Submission'])),
            ('medtech_reference_substance', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_statalgorithm', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('subject_duration_active', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('submitter_is_coordinator', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('sponsor_name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True)),
            ('sponsor_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('subject_duration', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('pharma_reference_substance', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project_type_questionnaire', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_is_main_investigator', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('insurance_phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('study_plan_population_intention_to_treat', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('submitter_is_authorized_by_sponsor', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('medtech_manufacturer', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('subject_planned_total_duration', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('project_type_medical_device_with_ce', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_is_sponsor', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_summary', self.gf('django.db.models.fields.TextField')(null=True)),
            ('insurance_contract_number', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('study_plan_power', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('sponsor_phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('subject_maxage', self.gf('django.db.models.fields.IntegerField')()),
            ('subject_noncompetents', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date_of_receipt', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('project_type_medical_device_without_ce', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('invoice_phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('german_risks_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('additional_therapy_info', self.gf('django.db.models.fields.TextField')()),
            ('specialism', self.gf('django.db.models.fields.TextField')(null=True)),
            ('study_plan_population_per_protocol', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('medtech_certified_for_other_indications', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('study_plan_parallelgroups', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_payment_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('study_plan_controlled', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_dataprotection_anonalgoritm', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_ethical_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_inclusion_exclusion_crit', self.gf('django.db.models.fields.TextField')(null=True)),
            ('medtech_technical_safety_regulations', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_pilot_project', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_number_of_groups', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('insurance_name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('study_plan_null_hypothesis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('clinical_phase', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('substance_preexisting_clinical_tries', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('substance_p_c_t_phase', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('subject_males', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('substance_p_c_t_period', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_benefits_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_abort_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('insurance_address_1', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('german_additional_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_primary_objectives', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sponsor_contactname', self.gf('django.db.models.fields.CharField')(max_length=80, null=True)),
            ('study_plan_dataprotection_reason', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('medtech_certified_for_exact_indications', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('sponsor_city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('medtech_manual_included', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('submitter_agrees_to_publishing', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('study_plan_alternative_hypothesis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('medtech_checked_product', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_sample_frequency', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_dataquality_checking', self.gf('django.db.models.fields.TextField')()),
            ('project_type_non_reg_drug', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_relationship_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('project_title', self.gf('django.db.models.fields.TextField')()),
            ('invoice_fax', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('sponsor_zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('insurance_validity', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('already_voted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_duration_controls', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('study_plan_dataprotection_dvr', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('german_sideeffects_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('subject_females', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('pharma_checked_substance', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project_type_misc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('invoice_city', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('german_financing_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('project_type_register', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_dataaccess_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project_type_biobank', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_observer_blinded', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('substance_p_c_t_application_type', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('invoice_zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('project_type_reg_drug_within_indication', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('invoice_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('study_plan_datamanagement', self.gf('django.db.models.fields.TextField')()),
            ('german_primary_hypothesis', self.gf('django.db.models.fields.TextField')(null=True)),
            ('subject_childbearing', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('substance_p_c_t_countries', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('study_plan_stratification', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project_type_reg_drug_not_within_indication', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_medical_method', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_education_context', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('invoice_address1', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('invoice_address2', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('study_plan_equivalence_testing', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_count', self.gf('django.db.models.fields.IntegerField')()),
            ('substance_p_c_t_gcp_rules', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('subject_minage', self.gf('django.db.models.fields.IntegerField')()),
            ('study_plan_randomized', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_cross_over', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('german_consent_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('medtech_departure_from_regulations', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_project_title', self.gf('django.db.models.fields.TextField')(null=True)),
            ('submitter_organisation', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('study_plan_multiple_test_correction_algorithm', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('sponsor_address1', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('invoice_name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('invoice_contactname', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('sponsor_address2', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('german_statistical_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['SubmissionForm'])

        # Adding M2M table for field documents on 'SubmissionForm'
        db.create_table('core_submissionform_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submissionform', models.ForeignKey(orm['core.submissionform'], null=False)),
            ('document', models.ForeignKey(orm['core.document'], null=False))
        ))
        db.create_unique('core_submissionform_documents', ['submissionform_id', 'document_id'])

        # Adding model 'Investigator'
        db.create_table('core_investigator', (
            ('specialist', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('sign_date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='investigators', to=orm['core.SubmissionForm'])),
            ('subject_count', self.gf('django.db.models.fields.IntegerField')()),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('ethics_commission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='investigators', null=True, to=orm['core.EthicsCommission'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('jus_practicandi', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('main', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('certified', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('core', ['Investigator'])

        # Adding model 'InvestigatorEmployee'
        db.create_table('core_investigatoremployee', (
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Investigator'])),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['InvestigatorEmployee'])

        # Adding model 'Measure'
        db.create_table('core_measure', (
            ('category', self.gf('django.db.models.fields.CharField')(max_length=3, null=True)),
            ('count', self.gf('django.db.models.fields.TextField')()),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='measures', to=orm['core.SubmissionForm'])),
            ('period', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('total', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Measure'])

        # Adding model 'NonTestedUsedDrug'
        db.create_table('core_nontesteduseddrug', (
            ('generic_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('preparation_form', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionForm'])),
            ('dosage', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('core', ['NonTestedUsedDrug'])

        # Adding model 'ForeignParticipatingCenter'
        db.create_table('core_foreignparticipatingcenter', (
            ('city', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionForm'])),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('core', ['ForeignParticipatingCenter'])

        # Adding model 'Amendment'
        db.create_table('core_amendment', (
            ('submissionform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionForm'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('core', ['Amendment'])

        # Adding model 'NotificationType'
        db.create_table('core_notificationtype', (
            ('model', self.gf('django.db.models.fields.CharField')(default='ecs.core.models.Notification', max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.CharField')(default='ecs.core.forms.NotificationForm', max_length=80)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
        ))
        db.send_create_signal('core', ['NotificationType'])

        # Adding model 'Notification'
        db.create_table('core_notification', (
            ('date_of_receipt', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', null=True, to=orm['core.NotificationType'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('core', ['Notification'])

        # Adding M2M table for field submission_forms on 'Notification'
        db.create_table('core_notification_submission_forms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification', models.ForeignKey(orm['core.notification'], null=False)),
            ('submissionform', models.ForeignKey(orm['core.submissionform'], null=False))
        ))
        db.create_unique('core_notification_submission_forms', ['notification_id', 'submissionform_id'])

        # Adding M2M table for field documents on 'Notification'
        db.create_table('core_notification_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification', models.ForeignKey(orm['core.notification'], null=False)),
            ('document', models.ForeignKey(orm['core.document'], null=False))
        ))
        db.create_unique('core_notification_documents', ['notification_id', 'document_id'])

        # Adding M2M table for field investigators on 'Notification'
        db.create_table('core_notification_investigators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification', models.ForeignKey(orm['core.notification'], null=False)),
            ('investigator', models.ForeignKey(orm['core.investigator'], null=False))
        ))
        db.create_unique('core_notification_investigators', ['notification_id', 'investigator_id'])

        # Adding model 'CompletionReportNotification'
        db.create_table('core_completionreportnotification', (
            ('finished_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('SAE_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('study_aborted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('recruited_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('reason_for_not_started', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('aborted_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('completion_date', self.gf('django.db.models.fields.DateField')()),
            ('SUSAR_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Notification'], unique=True)),
        ))
        db.send_create_signal('core', ['CompletionReportNotification'])

        # Adding model 'ProgressReportNotification'
        db.create_table('core_progressreportnotification', (
            ('finished_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('SAE_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('recruited_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('reason_for_not_started', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('aborted_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('runs_till', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('extension_of_vote_requested', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('SUSAR_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Notification'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['ProgressReportNotification'])

        # Adding model 'Checklist'
        db.create_table('core_checklist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Checklist'])

        # Adding model 'VoteReview'
        db.create_table('core_votereview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Workflow'])),
        ))
        db.send_create_signal('core', ['VoteReview'])

        # Adding model 'Vote'
        db.create_table('core_vote', (
            ('submissionform', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionForm'], null=True)),
            ('votereview', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.VoteReview'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Workflow'])),
        ))
        db.send_create_signal('core', ['Vote'])

        # Adding M2M table for field checklists on 'Vote'
        db.create_table('core_vote_checklists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vote', models.ForeignKey(orm['core.vote'], null=False)),
            ('checklist', models.ForeignKey(orm['core.checklist'], null=False))
        ))
        db.create_unique('core_vote_checklists', ['vote_id', 'checklist_id'])

        # Adding model 'SubmissionReview'
        db.create_table('core_submissionreview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Workflow'])),
        ))
        db.send_create_signal('core', ['SubmissionReview'])

        # Adding model 'Submission'
        db.create_table('core_submission', (
            ('submissionreview', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionReview'], null=True)),
            ('vote', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Vote'], null=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Workflow'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ec_number', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Submission'])

        # Adding model 'NotificationAnswer'
        db.create_table('core_notificationanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Workflow'])),
        ))
        db.send_create_signal('core', ['NotificationAnswer'])

        # Adding model 'Meeting'
        db.create_table('core_meeting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['Meeting'])

        # Adding M2M table for field submissions on 'Meeting'
        db.create_table('core_meeting_submissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meeting', models.ForeignKey(orm['core.meeting'], null=False)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False))
        ))
        db.create_unique('core_meeting_submissions', ['meeting_id', 'submission_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Workflow'
        db.delete_table('core_workflow')

        # Deleting model 'DocumentType'
        db.delete_table('core_documenttype')

        # Deleting model 'Document'
        db.delete_table('core_document')

        # Deleting model 'EthicsCommission'
        db.delete_table('core_ethicscommission')

        # Deleting model 'SubmissionForm'
        db.delete_table('core_submissionform')

        # Removing M2M table for field documents on 'SubmissionForm'
        db.delete_table('core_submissionform_documents')

        # Deleting model 'Investigator'
        db.delete_table('core_investigator')

        # Deleting model 'InvestigatorEmployee'
        db.delete_table('core_investigatoremployee')

        # Deleting model 'Measure'
        db.delete_table('core_measure')

        # Deleting model 'NonTestedUsedDrug'
        db.delete_table('core_nontesteduseddrug')

        # Deleting model 'ForeignParticipatingCenter'
        db.delete_table('core_foreignparticipatingcenter')

        # Deleting model 'Amendment'
        db.delete_table('core_amendment')

        # Deleting model 'NotificationType'
        db.delete_table('core_notificationtype')

        # Deleting model 'Notification'
        db.delete_table('core_notification')

        # Removing M2M table for field submission_forms on 'Notification'
        db.delete_table('core_notification_submission_forms')

        # Removing M2M table for field documents on 'Notification'
        db.delete_table('core_notification_documents')

        # Removing M2M table for field investigators on 'Notification'
        db.delete_table('core_notification_investigators')

        # Deleting model 'CompletionReportNotification'
        db.delete_table('core_completionreportnotification')

        # Deleting model 'ProgressReportNotification'
        db.delete_table('core_progressreportnotification')

        # Deleting model 'Checklist'
        db.delete_table('core_checklist')

        # Deleting model 'VoteReview'
        db.delete_table('core_votereview')

        # Deleting model 'Vote'
        db.delete_table('core_vote')

        # Removing M2M table for field checklists on 'Vote'
        db.delete_table('core_vote_checklists')

        # Deleting model 'SubmissionReview'
        db.delete_table('core_submissionreview')

        # Deleting model 'Submission'
        db.delete_table('core_submission')

        # Deleting model 'NotificationAnswer'
        db.delete_table('core_notificationanswer')

        # Deleting model 'Meeting'
        db.delete_table('core_meeting')

        # Removing M2M table for field submissions on 'Meeting'
        db.delete_table('core_meeting_submissions')
    
    
    models = {
        'core.amendment': {
            'Meta': {'object_name': 'Amendment'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'submissionform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.completionreportnotification': {
            'Meta': {'object_name': 'CompletionReportNotification'},
            'SAE_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'SUSAR_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'aborted_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'completion_date': ('django.db.models.fields.DateField', [], {}),
            'finished_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Notification']", 'unique': 'True'}),
            'reason_for_not_started': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recruited_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'study_aborted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'core.document': {
            'Meta': {'object_name': 'Document'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'doctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DocumentType']", 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'application/pdf'", 'max_length': '100'}),
            'original_file_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'uuid_document': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'uuid_document_revision': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'core.documenttype': {
            'Meta': {'object_name': 'DocumentType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.ethicscommission': {
            'Meta': {'object_name': 'EthicsCommission'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'chairperson': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'contactname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.foreignparticipatingcenter': {
            'Meta': {'object_name': 'ForeignParticipatingCenter'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.investigator': {
            'Meta': {'object_name': 'Investigator'},
            'certified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ethics_commission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigators'", 'null': 'True', 'to': "orm['core.EthicsCommission']"}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jus_practicandi': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'main': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sign_date': ('django.db.models.fields.DateField', [], {}),
            'specialist': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigators'", 'to': "orm['core.SubmissionForm']"})
        },
        'core.investigatoremployee': {
            'Meta': {'object_name': 'InvestigatorEmployee'},
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Investigator']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'core.measure': {
            'Meta': {'object_name': 'Measure'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'count': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'measures'", 'to': "orm['core.SubmissionForm']"}),
            'total': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'core.meeting': {
            'Meta': {'object_name': 'Meeting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Submission']"})
        },
        'core.nontesteduseddrug': {
            'Meta': {'object_name': 'NonTestedUsedDrug'},
            'dosage': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'generic_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preparation_form': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.notification': {
            'Meta': {'object_name': 'Notification'},
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'date_of_receipt': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'to': "orm['core.Investigator']"}),
            'submission_forms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'to': "orm['core.SubmissionForm']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'null': 'True', 'to': "orm['core.NotificationType']"})
        },
        'core.notificationanswer': {
            'Meta': {'object_name': 'NotificationAnswer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.notificationtype': {
            'Meta': {'object_name': 'NotificationType'},
            'form': ('django.db.models.fields.CharField', [], {'default': "'ecs.core.forms.NotificationForm'", 'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'default': "'ecs.core.models.Notification'", 'max_length': '80'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        'core.progressreportnotification': {
            'Meta': {'object_name': 'ProgressReportNotification'},
            'SAE_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'SUSAR_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'aborted_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'extension_of_vote_requested': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'finished_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'notification_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Notification']", 'unique': 'True', 'primary_key': 'True'}),
            'reason_for_not_started': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recruited_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'runs_till': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.submission': {
            'Meta': {'object_name': 'Submission'},
            'ec_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionreview': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionReview']", 'null': 'True'}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Vote']", 'null': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']", 'null': 'True'})
        },
        'core.submissionform': {
            'Meta': {'object_name': 'SubmissionForm'},
            'additional_therapy_info': ('django.db.models.fields.TextField', [], {}),
            'already_voted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'clinical_phase': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'date_of_receipt': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']"}),
            'ethics_commissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'submission_forms'", 'through': "'Investigator'", 'to': "orm['core.EthicsCommission']"}),
            'eudract_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'german_abort_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_aftercare_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_benefits_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_concurrent_study_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_consent_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_dataaccess_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_dataprotection_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_ethical_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_financing_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_inclusion_exclusion_crit': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_payment_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_preclinical_results': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_primary_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_project_title': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_protected_subjects_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_recruitment_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_relationship_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_risks_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_sideeffects_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_statistical_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_summary': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insurance_address_1': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'insurance_contract_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'insurance_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'insurance_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'insurance_validity': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'invoice_contactname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'invoice_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'invoice_fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'invoice_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'invoice_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'invoice_uid': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'invoice_uid_verified_level1': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'invoice_uid_verified_level2': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'invoice_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'medtech_ce_symbol': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_certified_for_exact_indications': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_certified_for_other_indications': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_checked_product': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_departure_from_regulations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_manual_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'medtech_product_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'medtech_reference_substance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_technical_safety_regulations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pharma_checked_substance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pharma_reference_substance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'project_title': ('django.db.models.fields.TextField', [], {}),
            'project_type_basic_research': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_biobank': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_education_context': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'project_type_genetic_study': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_medical_device': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_medical_device_performance_evaluation': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_medical_device_with_ce': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_medical_device_without_ce': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_medical_method': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_misc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'project_type_non_reg_drug': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_questionnaire': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_reg_drug': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_reg_drug_not_within_indication': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_reg_drug_within_indication': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_register': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_retrospective': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'specialism': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'sponsor_address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'sponsor_address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'sponsor_city': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'sponsor_contactname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'sponsor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'sponsor_fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sponsor_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'sponsor_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sponsor_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'study_plan_abort_crit': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_alpha': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_alternative_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_biometric_planning': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_blind': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'study_plan_controlled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_cross_over': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_datamanagement': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dataprotection_anonalgoritm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_dataprotection_dvr': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'study_plan_dataprotection_reason': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'study_plan_dataquality_checking': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dropout_ratio': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_equivalence_testing': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_factorized': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_misc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_multiple_test_correction_algorithm': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_null_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_number_of_groups': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_observer_blinded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_parallelgroups': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_pilot_project': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_placebo': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_planned_statalgorithm': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_population_intention_to_treat': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_population_per_protocol': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_power': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_primary_objectives': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_randomized': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_sample_frequency': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_secondary_objectives': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_statalgorithm': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_statistics_implementation': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_stratification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject_childbearing': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'subject_duration': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subject_duration_active': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subject_duration_controls': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'subject_females': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_males': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_maxage': ('django.db.models.fields.IntegerField', [], {}),
            'subject_minage': ('django.db.models.fields.IntegerField', [], {}),
            'subject_noncompetents': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_planned_total_duration': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forms'", 'to': "orm['core.Submission']"}),
            'submitter_agrees_to_publishing': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'submitter_is_authorized_by_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_coordinator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_main_investigator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'substance_p_c_t_application_type': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_countries': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_final_report': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_gcp_rules': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_period': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_phase': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'substance_preexisting_clinical_tries': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_registered_in_countries': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'})
        },
        'core.submissionreview': {
            'Meta': {'object_name': 'SubmissionReview'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.vote': {
            'Meta': {'object_name': 'Vote'},
            'checklists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Checklist']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']", 'null': 'True'}),
            'votereview': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.VoteReview']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.votereview': {
            'Meta': {'object_name': 'VoteReview'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['core']
