# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Submission'
        db.create_table('core_submission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ec_number', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=50, unique=True, null=True, blank=True)),
            ('thesis', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('retrospective', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('expedited', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('external_reviewer', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('external_reviewer_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('sponsor_required_for_next_meeting', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('core', ['Submission'])

        # Adding M2M table for field medical_categories on 'Submission'
        db.create_table('core_submission_medical_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('medicalcategory', models.ForeignKey(orm['core.medicalcategory'], null=False))
        ))
        db.create_unique('core_submission_medical_categories', ['submission_id', 'medicalcategory_id'])

        # Adding M2M table for field expedited_review_categories on 'Submission'
        db.create_table('core_submission_expedited_review_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('expeditedreviewcategory', models.ForeignKey(orm['core.expeditedreviewcategory'], null=False))
        ))
        db.create_unique('core_submission_expedited_review_categories', ['submission_id', 'expeditedreviewcategory_id'])

        # Adding M2M table for field additional_reviewers on 'Submission'
        db.create_table('core_submission_additional_reviewers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submission', models.ForeignKey(orm['core.submission'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('core_submission_additional_reviewers', ['submission_id', 'user_id'])

        # Adding model 'SubmissionForm'
        db.create_table('core_submissionform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forms', to=orm['core.Submission'])),
            ('project_title', self.gf('django.db.models.fields.TextField')()),
            ('eudract_number', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('sponsor_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('sponsor_contactname', self.gf('django.db.models.fields.CharField')(max_length=80, null=True)),
            ('sponsor_address1', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('sponsor_address2', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('sponsor_zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('sponsor_city', self.gf('django.db.models.fields.CharField')(max_length=80, null=True)),
            ('sponsor_phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('sponsor_fax', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('sponsor_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('invoice_name', self.gf('django.db.models.fields.CharField')(max_length=160, null=True, blank=True)),
            ('invoice_contactname', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('invoice_address1', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('invoice_address2', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('invoice_zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('invoice_city', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('invoice_phone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('invoice_fax', self.gf('django.db.models.fields.CharField')(max_length=45, null=True, blank=True)),
            ('invoice_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('invoice_uid', self.gf('django.db.models.fields.CharField')(max_length=35, null=True, blank=True)),
            ('invoice_uid_verified_level1', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('invoice_uid_verified_level2', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('project_type_non_reg_drug', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_reg_drug', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_reg_drug_within_indication', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_reg_drug_not_within_indication', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_medical_method', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_medical_device', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_medical_device_with_ce', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_medical_device_without_ce', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_medical_device_performance_evaluation', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_basic_research', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_genetic_study', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_register', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_biobank', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_retrospective', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_questionnaire', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('project_type_education_context', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('project_type_misc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project_type_psychological_study', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('specialism', self.gf('django.db.models.fields.TextField')(null=True)),
            ('pharma_checked_substance', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pharma_reference_substance', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('medtech_checked_product', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('medtech_reference_substance', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('clinical_phase', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('already_voted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_count', self.gf('django.db.models.fields.IntegerField')()),
            ('subject_minage', self.gf('django.db.models.fields.IntegerField')()),
            ('subject_maxage', self.gf('django.db.models.fields.IntegerField')()),
            ('subject_noncompetents', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_males', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_females', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_childbearing', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_duration', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject_duration_active', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject_duration_controls', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject_planned_total_duration', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('substance_preexisting_clinical_tries', self.gf('django.db.models.fields.NullBooleanField')(null=True, db_column='existing_tries', blank=True)),
            ('substance_p_c_t_phase', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('substance_p_c_t_period', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('substance_p_c_t_application_type', self.gf('django.db.models.fields.CharField')(max_length=145, null=True, blank=True)),
            ('substance_p_c_t_gcp_rules', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('substance_p_c_t_final_report', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('medtech_product_name', self.gf('django.db.models.fields.CharField')(max_length=210, null=True, blank=True)),
            ('medtech_manufacturer', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('medtech_certified_for_exact_indications', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('medtech_certified_for_other_indications', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('medtech_ce_symbol', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('medtech_manual_included', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('medtech_technical_safety_regulations', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('medtech_departure_from_regulations', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('insurance_name', self.gf('django.db.models.fields.CharField')(max_length=125, null=True, blank=True)),
            ('insurance_address_1', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('insurance_phone', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('insurance_contract_number', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('insurance_validity', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('additional_therapy_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('german_project_title', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_summary', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_preclinical_results', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_primary_hypothesis', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_inclusion_exclusion_crit', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_ethical_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_protected_subjects_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_recruitment_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_consent_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_risks_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_benefits_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_relationship_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_concurrent_study_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_sideeffects_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_statistical_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_dataprotection_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_aftercare_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_payment_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_abort_info', self.gf('django.db.models.fields.TextField')(null=True)),
            ('german_dataaccess_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_financing_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('german_additional_info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_blind', self.gf('django.db.models.fields.SmallIntegerField')(null=True)),
            ('study_plan_observer_blinded', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_randomized', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_parallelgroups', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_controlled', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_cross_over', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_placebo', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_factorized', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_pilot_project', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_equivalence_testing', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_misc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_number_of_groups', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_stratification', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_sample_frequency', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_primary_objectives', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_null_hypothesis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_alternative_hypothesis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_secondary_objectives', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_alpha', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('study_plan_power', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('study_plan_statalgorithm', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('study_plan_multiple_test_correction_algorithm', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('study_plan_dropout_ratio', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('study_plan_population_intention_to_treat', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_population_per_protocol', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('study_plan_abort_crit', self.gf('django.db.models.fields.CharField')(max_length=265)),
            ('study_plan_planned_statalgorithm', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_plan_dataquality_checking', self.gf('django.db.models.fields.TextField')()),
            ('study_plan_datamanagement', self.gf('django.db.models.fields.TextField')()),
            ('study_plan_biometric_planning', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('study_plan_statistics_implementation', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('study_plan_dataprotection_reason', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('study_plan_dataprotection_dvr', self.gf('django.db.models.fields.CharField')(max_length=180, blank=True)),
            ('study_plan_dataprotection_anonalgoritm', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('submitter_name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('submitter_organisation', self.gf('django.db.models.fields.CharField')(max_length=180)),
            ('submitter_jobtitle', self.gf('django.db.models.fields.CharField')(max_length=130)),
            ('submitter_is_coordinator', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_is_main_investigator', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_is_sponsor', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_is_authorized_by_sponsor', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submitter_agrees_to_publishing', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('date_of_receipt', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['SubmissionForm'])

        # Adding M2M table for field documents on 'SubmissionForm'
        db.create_table('core_submissionform_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submissionform', models.ForeignKey(orm['core.submissionform'], null=False)),
            ('document', models.ForeignKey(orm['core.document'], null=False))
        ))
        db.create_unique('core_submissionform_documents', ['submissionform_id', 'document_id'])

        # Adding M2M table for field substance_registered_in_countries on 'SubmissionForm'
        db.create_table('submission_registered_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submissionform', models.ForeignKey(orm['core.submissionform'], null=False)),
            ('country', models.ForeignKey(orm['countries.country'], null=False))
        ))
        db.create_unique('submission_registered_countries', ['submissionform_id', 'country_id'])

        # Adding M2M table for field substance_p_c_t_countries on 'SubmissionForm'
        db.create_table('core_submissionform_substance_p_c_t_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submissionform', models.ForeignKey(orm['core.submissionform'], null=False)),
            ('country', models.ForeignKey(orm['countries.country'], null=False))
        ))
        db.create_unique('core_submissionform_substance_p_c_t_countries', ['submissionform_id', 'country_id'])

        # Adding model 'Investigator'
        db.create_table('core_investigator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='investigators', to=orm['core.SubmissionForm'])),
            ('ethics_commission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='investigators', null=True, to=orm['core.EthicsCommission'])),
            ('main', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('mobile', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('jus_practicandi', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('specialist', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('certified', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('subject_count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('core', ['Investigator'])

        # Adding model 'InvestigatorEmployee'
        db.create_table('core_investigatoremployee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('investigator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Investigator'])),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('core', ['InvestigatorEmployee'])

        # Adding model 'Measure'
        db.create_table('core_measure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='measures', to=orm['core.SubmissionForm'])),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=3, null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('count', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('period', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('total', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('core', ['Measure'])

        # Adding model 'NonTestedUsedDrug'
        db.create_table('core_nontesteduseddrug', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionForm'])),
            ('generic_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('preparation_form', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('dosage', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('core', ['NonTestedUsedDrug'])

        # Adding model 'ForeignParticipatingCenter'
        db.create_table('core_foreignparticipatingcenter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission_form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.SubmissionForm'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('investigator_name', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
        ))
        db.send_create_signal('core', ['ForeignParticipatingCenter'])

        # Adding model 'ChecklistBlueprint'
        db.create_table('core_checklistblueprint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('core', ['ChecklistBlueprint'])

        # Adding model 'ChecklistQuestion'
        db.create_table('core_checklistquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('blueprint', self.gf('django.db.models.fields.related.ForeignKey')(related_name='questions', to=orm['core.ChecklistBlueprint'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['ChecklistQuestion'])

        # Adding model 'Checklist'
        db.create_table('core_checklist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('blueprint', self.gf('django.db.models.fields.related.ForeignKey')(related_name='checklists', to=orm['core.ChecklistBlueprint'])),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='checklists', null=True, to=orm['core.Submission'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('core', ['Checklist'])

        # Adding model 'ChecklistAnswer'
        db.create_table('core_checklistanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('checklist', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['core.Checklist'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.ChecklistQuestion'])),
            ('answer', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['ChecklistAnswer'])

        # Adding model 'EthicsCommission'
        db.create_table('core_ethicscommission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('contactname', self.gf('django.db.models.fields.CharField')(max_length=120, null=True)),
            ('chairperson', self.gf('django.db.models.fields.CharField')(max_length=120, null=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
        ))
        db.send_create_signal('core', ['EthicsCommission'])

        # Adding model 'ExpeditedReviewCategory'
        db.create_table('core_expeditedreviewcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=12)),
        ))
        db.send_create_signal('core', ['ExpeditedReviewCategory'])

        # Adding model 'MedicalCategory'
        db.create_table('core_medicalcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=12)),
        ))
        db.send_create_signal('core', ['MedicalCategory'])

        # Adding M2M table for field users on 'MedicalCategory'
        db.create_table('core_medicalcategory_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('medicalcategory', models.ForeignKey(orm['core.medicalcategory'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('core_medicalcategory_users', ['medicalcategory_id', 'user_id'])

        # Adding model 'DocumentType'
        db.create_table('core_documenttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('core', ['DocumentType'])

        # Adding model 'Document'
        db.create_table('core_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid_document', self.gf('django.db.models.fields.SlugField')(max_length=32, db_index=True)),
            ('uuid_document_revision', self.gf('django.db.models.fields.SlugField')(max_length=32, db_index=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('original_file_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('doctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.DocumentType'], null=True, blank=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(default='application/pdf', max_length=100)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('core', ['Document'])

        # Adding model 'NotificationType'
        db.create_table('core_notificationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('form', self.gf('django.db.models.fields.CharField')(default='ecs.core.forms.NotificationForm', max_length=80)),
        ))
        db.send_create_signal('core', ['NotificationType'])

        # Adding model 'Notification'
        db.create_table('core_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', null=True, to=orm['core.NotificationType'])),
            ('comments', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('date_of_receipt', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Notification'])

        # Adding M2M table for field investigators on 'Notification'
        db.create_table('core_notification_investigators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification', models.ForeignKey(orm['core.notification'], null=False)),
            ('investigator', models.ForeignKey(orm['core.investigator'], null=False))
        ))
        db.create_unique('core_notification_investigators', ['notification_id', 'investigator_id'])

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

        # Adding model 'CompletionReportNotification'
        db.create_table('core_completionreportnotification', (
            ('notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Notification'], unique=True)),
            ('reason_for_not_started', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('recruited_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('finished_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('aborted_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('SAE_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('SUSAR_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('study_aborted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('completion_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('core', ['CompletionReportNotification'])

        # Adding model 'ProgressReportNotification'
        db.create_table('core_progressreportnotification', (
            ('notification_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Notification'], unique=True, primary_key=True)),
            ('reason_for_not_started', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('recruited_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('finished_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('aborted_subjects', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('SAE_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('SUSAR_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('runs_till', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('extension_of_vote_requested', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('core', ['ProgressReportNotification'])

        # Adding model 'Meeting'
        db.create_table('core_meeting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('optimization_task_id', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('core', ['Meeting'])

        # Adding model 'TimetableEntry'
        db.create_table('core_timetableentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='timetable_entries', to=orm['core.Meeting'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('timetable_index', self.gf('django.db.models.fields.IntegerField')()),
            ('duration_in_seconds', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_break', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='timetable_entries', null=True, to=orm['core.Submission'])),
            ('sponsor_invited', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('optimal_start', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('core', ['TimetableEntry'])

        # Adding model 'Participation'
        db.create_table('core_participation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participations', to=orm['core.TimetableEntry'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meeting_participations', to=orm['auth.User'])),
            ('medical_category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='meeting_participations', null=True, to=orm['core.MedicalCategory'])),
        ))
        db.send_create_signal('core', ['Participation'])

        # Adding model 'Constraint'
        db.create_table('core_constraint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='constraints', to=orm['core.Meeting'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meeting_constraints', to=orm['auth.User'])),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.FloatField')(default=0.5)),
        ))
        db.send_create_signal('core', ['Constraint'])

        # Adding model 'UserProfile'
        db.create_table('core_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='ecs_profile', unique=True, to=orm['auth.User'])),
            ('external_review', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('board_member', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('executive_board_member', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('thesis_review', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('internal', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('core', ['UserProfile'])

        # Adding model 'Vote'
        db.create_table('core_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('top', self.gf('django.db.models.fields.related.OneToOneField')(related_name='vote', unique=True, to=orm['core.TimetableEntry'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('executive_review_required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('core', ['Vote'])


    def backwards(self, orm):
        
        # Deleting model 'Submission'
        db.delete_table('core_submission')

        # Removing M2M table for field medical_categories on 'Submission'
        db.delete_table('core_submission_medical_categories')

        # Removing M2M table for field expedited_review_categories on 'Submission'
        db.delete_table('core_submission_expedited_review_categories')

        # Removing M2M table for field additional_reviewers on 'Submission'
        db.delete_table('core_submission_additional_reviewers')

        # Deleting model 'SubmissionForm'
        db.delete_table('core_submissionform')

        # Removing M2M table for field documents on 'SubmissionForm'
        db.delete_table('core_submissionform_documents')

        # Removing M2M table for field substance_registered_in_countries on 'SubmissionForm'
        db.delete_table('submission_registered_countries')

        # Removing M2M table for field substance_p_c_t_countries on 'SubmissionForm'
        db.delete_table('core_submissionform_substance_p_c_t_countries')

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

        # Deleting model 'ChecklistBlueprint'
        db.delete_table('core_checklistblueprint')

        # Deleting model 'ChecklistQuestion'
        db.delete_table('core_checklistquestion')

        # Deleting model 'Checklist'
        db.delete_table('core_checklist')

        # Deleting model 'ChecklistAnswer'
        db.delete_table('core_checklistanswer')

        # Deleting model 'EthicsCommission'
        db.delete_table('core_ethicscommission')

        # Deleting model 'ExpeditedReviewCategory'
        db.delete_table('core_expeditedreviewcategory')

        # Deleting model 'MedicalCategory'
        db.delete_table('core_medicalcategory')

        # Removing M2M table for field users on 'MedicalCategory'
        db.delete_table('core_medicalcategory_users')

        # Deleting model 'DocumentType'
        db.delete_table('core_documenttype')

        # Deleting model 'Document'
        db.delete_table('core_document')

        # Deleting model 'NotificationType'
        db.delete_table('core_notificationtype')

        # Deleting model 'Notification'
        db.delete_table('core_notification')

        # Removing M2M table for field investigators on 'Notification'
        db.delete_table('core_notification_investigators')

        # Removing M2M table for field submission_forms on 'Notification'
        db.delete_table('core_notification_submission_forms')

        # Removing M2M table for field documents on 'Notification'
        db.delete_table('core_notification_documents')

        # Deleting model 'CompletionReportNotification'
        db.delete_table('core_completionreportnotification')

        # Deleting model 'ProgressReportNotification'
        db.delete_table('core_progressreportnotification')

        # Deleting model 'Meeting'
        db.delete_table('core_meeting')

        # Deleting model 'TimetableEntry'
        db.delete_table('core_timetableentry')

        # Deleting model 'Participation'
        db.delete_table('core_participation')

        # Deleting model 'Constraint'
        db.delete_table('core_constraint')

        # Deleting model 'UserProfile'
        db.delete_table('core_userprofile')

        # Deleting model 'Vote'
        db.delete_table('core_vote')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.checklist': {
            'Meta': {'object_name': 'Checklist'},
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'checklists'", 'to': "orm['core.ChecklistBlueprint']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'checklists'", 'null': 'True', 'to': "orm['core.Submission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'core.checklistanswer': {
            'Meta': {'object_name': 'ChecklistAnswer'},
            'answer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'checklist': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['core.Checklist']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.ChecklistQuestion']"})
        },
        'core.checklistblueprint': {
            'Meta': {'object_name': 'ChecklistBlueprint'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.checklistquestion': {
            'Meta': {'object_name': 'ChecklistQuestion'},
            'blueprint': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['core.ChecklistBlueprint']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
        'core.constraint': {
            'Meta': {'object_name': 'Constraint'},
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'constraints'", 'to': "orm['core.Meeting']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_constraints'", 'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.5'})
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
        'core.expeditedreviewcategory': {
            'Meta': {'object_name': 'ExpeditedReviewCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'core.foreignparticipatingcenter': {
            'Meta': {'object_name': 'ForeignParticipatingCenter'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
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
            'specialist': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigators'", 'to': "orm['core.SubmissionForm']"})
        },
        'core.investigatoremployee': {
            'Meta': {'object_name': 'InvestigatorEmployee'},
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Investigator']"}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'core.measure': {
            'Meta': {'object_name': 'Measure'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'count': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'measures'", 'to': "orm['core.SubmissionForm']"}),
            'total': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'core.medicalcategory': {
            'Meta': {'object_name': 'MedicalCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'medical_categories'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'core.meeting': {
            'Meta': {'object_name': 'Meeting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optimization_task_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'submissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'meetings'", 'symmetrical': 'False', 'through': "orm['core.TimetableEntry']", 'to': "orm['core.Submission']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
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
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'symmetrical': 'False', 'to': "orm['core.Investigator']"}),
            'submission_forms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifications'", 'symmetrical': 'False', 'to': "orm['core.SubmissionForm']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'null': 'True', 'to': "orm['core.NotificationType']"})
        },
        'core.notificationtype': {
            'Meta': {'object_name': 'NotificationType'},
            'form': ('django.db.models.fields.CharField', [], {'default': "'ecs.core.forms.NotificationForm'", 'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        'core.participation': {
            'Meta': {'object_name': 'Participation'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participations'", 'to': "orm['core.TimetableEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meeting_participations'", 'null': 'True', 'to': "orm['core.MedicalCategory']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_participations'", 'to': "orm['auth.User']"})
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
            'additional_reviewers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'additional_review_submission_set'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'ec_number': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'expedited': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'expedited_review_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.ExpeditedReviewCategory']"}),
            'external_reviewer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'external_reviewer_name': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.MedicalCategory']"}),
            'retrospective': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'sponsor_required_for_next_meeting': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'thesis': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.submissionform': {
            'Meta': {'object_name': 'SubmissionForm'},
            'additional_therapy_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'already_voted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'clinical_phase': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'date_of_receipt': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']", 'symmetrical': 'False'}),
            'ethics_commissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'submission_forms'", 'symmetrical': 'False', 'through': "orm['core.Investigator']", 'to': "orm['core.EthicsCommission']"}),
            'eudract_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'german_abort_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_aftercare_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_benefits_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_concurrent_study_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_consent_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_dataaccess_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_dataprotection_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_ethical_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_financing_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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
            'insurance_name': ('django.db.models.fields.CharField', [], {'max_length': '125', 'null': 'True', 'blank': 'True'}),
            'insurance_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'insurance_validity': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'invoice_contactname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'invoice_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'invoice_fax': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'invoice_name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'invoice_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'invoice_uid': ('django.db.models.fields.CharField', [], {'max_length': '35', 'null': 'True', 'blank': 'True'}),
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
            'medtech_product_name': ('django.db.models.fields.CharField', [], {'max_length': '210', 'null': 'True', 'blank': 'True'}),
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
            'project_type_psychological_study': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_questionnaire': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_reg_drug': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_reg_drug_not_within_indication': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_reg_drug_within_indication': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_register': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_retrospective': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'specialism': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'sponsor_address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'sponsor_address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'sponsor_city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'sponsor_contactname': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'sponsor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'sponsor_fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sponsor_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'sponsor_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sponsor_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'study_plan_abort_crit': ('django.db.models.fields.CharField', [], {'max_length': '265'}),
            'study_plan_alpha': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_alternative_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_biometric_planning': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_blind': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'study_plan_controlled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_cross_over': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_datamanagement': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dataprotection_anonalgoritm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_dataprotection_dvr': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'study_plan_dataprotection_reason': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'study_plan_dataquality_checking': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dropout_ratio': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_equivalence_testing': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_factorized': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_misc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_multiple_test_correction_algorithm': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'study_plan_null_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_number_of_groups': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_observer_blinded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_parallelgroups': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_pilot_project': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_placebo': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_planned_statalgorithm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_population_intention_to_treat': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_population_per_protocol': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_power': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_primary_objectives': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_randomized': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_sample_frequency': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_secondary_objectives': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_statalgorithm': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'study_plan_statistics_implementation': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_stratification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject_childbearing': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'subject_duration': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_duration_active': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_duration_controls': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_females': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_males': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_maxage': ('django.db.models.fields.IntegerField', [], {}),
            'subject_minage': ('django.db.models.fields.IntegerField', [], {}),
            'subject_noncompetents': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subject_planned_total_duration': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forms'", 'to': "orm['core.Submission']"}),
            'submitter_agrees_to_publishing': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'submitter_is_authorized_by_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_coordinator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_main_investigator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '130'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_organisation': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'substance_p_c_t_application_type': ('django.db.models.fields.CharField', [], {'max_length': '145', 'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['countries.Country']", 'symmetrical': 'False', 'blank': 'True'}),
            'substance_p_c_t_final_report': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_gcp_rules': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_period': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_phase': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'substance_preexisting_clinical_tries': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'db_column': "'existing_tries'", 'blank': 'True'}),
            'substance_registered_in_countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submission_forms'", 'blank': 'True', 'db_table': "'submission_registered_countries'", 'to': "orm['countries.Country']"})
        },
        'core.timetableentry': {
            'Meta': {'object_name': 'TimetableEntry'},
            'duration_in_seconds': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_break': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'timetable_entries'", 'to': "orm['core.Meeting']"}),
            'optimal_start': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'sponsor_invited': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'timetable_entries'", 'null': 'True', 'to': "orm['core.Submission']"}),
            'timetable_index': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'board_member': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'executive_board_member': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'external_review': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'thesis_review': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ecs_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'core.vote': {
            'Meta': {'object_name': 'Vote'},
            'executive_review_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'top': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'vote'", 'unique': 'True', 'to': "orm['core.TimetableEntry']"})
        },
        'countries.country': {
            'Meta': {'object_name': 'Country', 'db_table': "'country'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['core']
