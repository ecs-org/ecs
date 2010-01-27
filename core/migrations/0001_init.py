# -*- coding: utf-8 -*- 

from south.db import db
from django.db import models
from core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Vote'
        db.create_table('core_vote', (
            ('id', orm['core.Vote:id']),
            ('votereview', orm['core.Vote:votereview']),
            ('submissionset', orm['core.Vote:submissionset']),
            ('workflow', orm['core.Vote:workflow']),
        ))
        db.send_create_signal('core', ['Vote'])
        
        # Adding model 'DiagnosticsApplied'
        db.create_table('core_diagnosticsapplied', (
            ('id', orm['core.DiagnosticsApplied:id']),
            ('submission', orm['core.DiagnosticsApplied:submission']),
            ('type', orm['core.DiagnosticsApplied:type']),
            ('count', orm['core.DiagnosticsApplied:count']),
            ('period', orm['core.DiagnosticsApplied:period']),
            ('total', orm['core.DiagnosticsApplied:total']),
        ))
        db.send_create_signal('core', ['DiagnosticsApplied'])
        
        # Adding model 'SubmissionReview'
        db.create_table('core_submissionreview', (
            ('id', orm['core.SubmissionReview:id']),
            ('workflow', orm['core.SubmissionReview:workflow']),
        ))
        db.send_create_signal('core', ['SubmissionReview'])
        
        # Adding model 'NonTestedUsedDrugs'
        db.create_table('core_nontesteduseddrugs', (
            ('id', orm['core.NonTestedUsedDrugs:id']),
            ('submission', orm['core.NonTestedUsedDrugs:submission']),
            ('generic_name', orm['core.NonTestedUsedDrugs:generic_name']),
            ('preparation_form', orm['core.NonTestedUsedDrugs:preparation_form']),
            ('dosage', orm['core.NonTestedUsedDrugs:dosage']),
        ))
        db.send_create_signal('core', ['NonTestedUsedDrugs'])
        
        # Adding model 'EthicsCommission'
        db.create_table('core_ethicscommission', (
            ('id', orm['core.EthicsCommission:id']),
            ('name', orm['core.EthicsCommission:name']),
            ('address_1', orm['core.EthicsCommission:address_1']),
            ('address_2', orm['core.EthicsCommission:address_2']),
            ('zip_code', orm['core.EthicsCommission:zip_code']),
            ('city', orm['core.EthicsCommission:city']),
        ))
        db.send_create_signal('core', ['EthicsCommission'])
        
        # Adding model 'Workflow'
        db.create_table('core_workflow', (
            ('id', orm['core.Workflow:id']),
        ))
        db.send_create_signal('core', ['Workflow'])
        
        # Adding model 'Checklist'
        db.create_table('core_checklist', (
            ('id', orm['core.Checklist:id']),
        ))
        db.send_create_signal('core', ['Checklist'])
        
        # Adding model 'Amendment'
        db.create_table('core_amendment', (
            ('id', orm['core.Amendment:id']),
            ('submissionform', orm['core.Amendment:submissionform']),
            ('order', orm['core.Amendment:order']),
            ('number', orm['core.Amendment:number']),
            ('date', orm['core.Amendment:date']),
        ))
        db.send_create_signal('core', ['Amendment'])
        
        # Adding model 'Document'
        db.create_table('core_document', (
            ('id', orm['core.Document:id']),
            ('uuid_document', orm['core.Document:uuid_document']),
            ('uuid_document_revision', orm['core.Document:uuid_document_revision']),
            ('version', orm['core.Document:version']),
            ('date', orm['core.Document:date']),
            ('absent', orm['core.Document:absent']),
        ))
        db.send_create_signal('core', ['Document'])
        
        # Adding model 'TherapiesApplied'
        db.create_table('core_therapiesapplied', (
            ('id', orm['core.TherapiesApplied:id']),
            ('submission', orm['core.TherapiesApplied:submission']),
            ('type', orm['core.TherapiesApplied:type']),
            ('count', orm['core.TherapiesApplied:count']),
            ('period', orm['core.TherapiesApplied:period']),
            ('total', orm['core.TherapiesApplied:total']),
        ))
        db.send_create_signal('core', ['TherapiesApplied'])
        
        # Adding model 'Investigator'
        db.create_table('core_investigator', (
            ('id', orm['core.Investigator:id']),
            ('submission', orm['core.Investigator:submission']),
            ('name', orm['core.Investigator:name']),
            ('organisation', orm['core.Investigator:organisation']),
            ('phone', orm['core.Investigator:phone']),
            ('mobile', orm['core.Investigator:mobile']),
            ('fax', orm['core.Investigator:fax']),
            ('email', orm['core.Investigator:email']),
            ('jus_practicandi', orm['core.Investigator:jus_practicandi']),
            ('specialist', orm['core.Investigator:specialist']),
            ('certified', orm['core.Investigator:certified']),
            ('subject_count', orm['core.Investigator:subject_count']),
            ('sign_date', orm['core.Investigator:sign_date']),
        ))
        db.send_create_signal('core', ['Investigator'])
        
        # Adding model 'SubmissionForm'
        db.create_table('core_submissionform', (
            ('id', orm['core.SubmissionForm:id']),
            ('project_title', orm['core.SubmissionForm:project_title']),
            ('protocol_number', orm['core.SubmissionForm:protocol_number']),
            ('date_of_protocol', orm['core.SubmissionForm:date_of_protocol']),
            ('eudract_number', orm['core.SubmissionForm:eudract_number']),
            ('isrctn_number', orm['core.SubmissionForm:isrctn_number']),
            ('sponsor_name', orm['core.SubmissionForm:sponsor_name']),
            ('sponsor_address1', orm['core.SubmissionForm:sponsor_address1']),
            ('sponsor_address2', orm['core.SubmissionForm:sponsor_address2']),
            ('sponsor_zip_code', orm['core.SubmissionForm:sponsor_zip_code']),
            ('sponsor_city', orm['core.SubmissionForm:sponsor_city']),
            ('sponsor_phone', orm['core.SubmissionForm:sponsor_phone']),
            ('sponsor_fax', orm['core.SubmissionForm:sponsor_fax']),
            ('sponsor_email', orm['core.SubmissionForm:sponsor_email']),
            ('invoice_name', orm['core.SubmissionForm:invoice_name']),
            ('invoice_address1', orm['core.SubmissionForm:invoice_address1']),
            ('invoice_address2', orm['core.SubmissionForm:invoice_address2']),
            ('invoice_zip_code', orm['core.SubmissionForm:invoice_zip_code']),
            ('invoice_city', orm['core.SubmissionForm:invoice_city']),
            ('invoice_phone', orm['core.SubmissionForm:invoice_phone']),
            ('invoice_fax', orm['core.SubmissionForm:invoice_fax']),
            ('invoice_email', orm['core.SubmissionForm:invoice_email']),
            ('invoice_uid', orm['core.SubmissionForm:invoice_uid']),
            ('invoice_uid_verified_level1', orm['core.SubmissionForm:invoice_uid_verified_level1']),
            ('invoice_uid_verified_level2', orm['core.SubmissionForm:invoice_uid_verified_level2']),
            ('project_type_2_1_1', orm['core.SubmissionForm:project_type_2_1_1']),
            ('project_type_2_1_2', orm['core.SubmissionForm:project_type_2_1_2']),
            ('project_type_2_1_2_1', orm['core.SubmissionForm:project_type_2_1_2_1']),
            ('project_type_2_1_2_2', orm['core.SubmissionForm:project_type_2_1_2_2']),
            ('project_type_2_1_3', orm['core.SubmissionForm:project_type_2_1_3']),
            ('project_type_2_1_4', orm['core.SubmissionForm:project_type_2_1_4']),
            ('project_type_2_1_4_1', orm['core.SubmissionForm:project_type_2_1_4_1']),
            ('project_type_2_1_4_2', orm['core.SubmissionForm:project_type_2_1_4_2']),
            ('project_type_2_1_4_3', orm['core.SubmissionForm:project_type_2_1_4_3']),
            ('project_type_2_1_5', orm['core.SubmissionForm:project_type_2_1_5']),
            ('project_type_2_1_6', orm['core.SubmissionForm:project_type_2_1_6']),
            ('project_type_2_1_7', orm['core.SubmissionForm:project_type_2_1_7']),
            ('project_type_2_1_8', orm['core.SubmissionForm:project_type_2_1_8']),
            ('project_type_2_1_9', orm['core.SubmissionForm:project_type_2_1_9']),
            ('specialism', orm['core.SubmissionForm:specialism']),
            ('pharma_checked_substance', orm['core.SubmissionForm:pharma_checked_substance']),
            ('pharma_reference_substance', orm['core.SubmissionForm:pharma_reference_substance']),
            ('medtech_checked_product', orm['core.SubmissionForm:medtech_checked_product']),
            ('medtech_reference_substance', orm['core.SubmissionForm:medtech_reference_substance']),
            ('clinical_phase', orm['core.SubmissionForm:clinical_phase']),
            ('already_voted', orm['core.SubmissionForm:already_voted']),
            ('subject_count', orm['core.SubmissionForm:subject_count']),
            ('subject_minage', orm['core.SubmissionForm:subject_minage']),
            ('subject_maxage', orm['core.SubmissionForm:subject_maxage']),
            ('subject_noncompetents', orm['core.SubmissionForm:subject_noncompetents']),
            ('subject_males', orm['core.SubmissionForm:subject_males']),
            ('subject_females', orm['core.SubmissionForm:subject_females']),
            ('subject_childbearing', orm['core.SubmissionForm:subject_childbearing']),
            ('subject_duration', orm['core.SubmissionForm:subject_duration']),
            ('subject_duration_active', orm['core.SubmissionForm:subject_duration_active']),
            ('subject_duration_controls', orm['core.SubmissionForm:subject_duration_controls']),
            ('subject_planned_total_duration', orm['core.SubmissionForm:subject_planned_total_duration']),
            ('substance_registered_in_countries', orm['core.SubmissionForm:substance_registered_in_countries']),
            ('substance_preexisting_clinical_tries', orm['core.SubmissionForm:substance_preexisting_clinical_tries']),
            ('substance_p_c_t_countries', orm['core.SubmissionForm:substance_p_c_t_countries']),
            ('substance_p_c_t_phase', orm['core.SubmissionForm:substance_p_c_t_phase']),
            ('substance_p_c_t_period', orm['core.SubmissionForm:substance_p_c_t_period']),
            ('substance_p_c_t_application_type', orm['core.SubmissionForm:substance_p_c_t_application_type']),
            ('substance_p_c_t_gcp_rules', orm['core.SubmissionForm:substance_p_c_t_gcp_rules']),
            ('substance_p_c_t_final_report', orm['core.SubmissionForm:substance_p_c_t_final_report']),
            ('medtech_product_name', orm['core.SubmissionForm:medtech_product_name']),
            ('medtech_manufacturer', orm['core.SubmissionForm:medtech_manufacturer']),
            ('medtech_certified_for_exact_indications', orm['core.SubmissionForm:medtech_certified_for_exact_indications']),
            ('medtech_certified_for_other_indications', orm['core.SubmissionForm:medtech_certified_for_other_indications']),
            ('medtech_ce_symbol', orm['core.SubmissionForm:medtech_ce_symbol']),
            ('medtech_manual_included', orm['core.SubmissionForm:medtech_manual_included']),
            ('medtech_technical_safety_regulations', orm['core.SubmissionForm:medtech_technical_safety_regulations']),
            ('medtech_departure_from_regulations', orm['core.SubmissionForm:medtech_departure_from_regulations']),
            ('insurance_name', orm['core.SubmissionForm:insurance_name']),
            ('insurance_address_1', orm['core.SubmissionForm:insurance_address_1']),
            ('insurance_phone', orm['core.SubmissionForm:insurance_phone']),
            ('insurance_contract_number', orm['core.SubmissionForm:insurance_contract_number']),
            ('insurance_validity', orm['core.SubmissionForm:insurance_validity']),
            ('additional_therapy_info', orm['core.SubmissionForm:additional_therapy_info']),
            ('german_project_title', orm['core.SubmissionForm:german_project_title']),
            ('german_summary', orm['core.SubmissionForm:german_summary']),
            ('german_preclinical_results', orm['core.SubmissionForm:german_preclinical_results']),
            ('german_primary_hypothesis', orm['core.SubmissionForm:german_primary_hypothesis']),
            ('german_inclusion_exclusion_crit', orm['core.SubmissionForm:german_inclusion_exclusion_crit']),
            ('german_ethical_info', orm['core.SubmissionForm:german_ethical_info']),
            ('german_protected_subjects_info', orm['core.SubmissionForm:german_protected_subjects_info']),
            ('german_recruitment_info', orm['core.SubmissionForm:german_recruitment_info']),
            ('german_consent_info', orm['core.SubmissionForm:german_consent_info']),
            ('german_risks_info', orm['core.SubmissionForm:german_risks_info']),
            ('german_benefits_info', orm['core.SubmissionForm:german_benefits_info']),
            ('german_relationship_info', orm['core.SubmissionForm:german_relationship_info']),
            ('german_concurrent_study_info', orm['core.SubmissionForm:german_concurrent_study_info']),
            ('german_sideeffects_info', orm['core.SubmissionForm:german_sideeffects_info']),
            ('german_statistical_info', orm['core.SubmissionForm:german_statistical_info']),
            ('german_dataprotection_info', orm['core.SubmissionForm:german_dataprotection_info']),
            ('german_aftercare_info', orm['core.SubmissionForm:german_aftercare_info']),
            ('german_payment_info', orm['core.SubmissionForm:german_payment_info']),
            ('german_abort_info', orm['core.SubmissionForm:german_abort_info']),
            ('german_dataaccess_info', orm['core.SubmissionForm:german_dataaccess_info']),
            ('german_financing_info', orm['core.SubmissionForm:german_financing_info']),
            ('german_additional_info', orm['core.SubmissionForm:german_additional_info']),
            ('study_plan_8_1_1', orm['core.SubmissionForm:study_plan_8_1_1']),
            ('study_plan_8_1_2', orm['core.SubmissionForm:study_plan_8_1_2']),
            ('study_plan_8_1_3', orm['core.SubmissionForm:study_plan_8_1_3']),
            ('study_plan_8_1_4', orm['core.SubmissionForm:study_plan_8_1_4']),
            ('study_plan_8_1_5', orm['core.SubmissionForm:study_plan_8_1_5']),
            ('study_plan_8_1_6', orm['core.SubmissionForm:study_plan_8_1_6']),
            ('study_plan_8_1_7', orm['core.SubmissionForm:study_plan_8_1_7']),
            ('study_plan_8_1_8', orm['core.SubmissionForm:study_plan_8_1_8']),
            ('study_plan_8_1_9', orm['core.SubmissionForm:study_plan_8_1_9']),
            ('study_plan_8_1_10', orm['core.SubmissionForm:study_plan_8_1_10']),
            ('study_plan_8_1_11', orm['core.SubmissionForm:study_plan_8_1_11']),
            ('study_plan_8_1_12', orm['core.SubmissionForm:study_plan_8_1_12']),
            ('study_plan_8_1_13', orm['core.SubmissionForm:study_plan_8_1_13']),
            ('study_plan_8_1_14', orm['core.SubmissionForm:study_plan_8_1_14']),
            ('study_plan_8_1_15', orm['core.SubmissionForm:study_plan_8_1_15']),
            ('study_plan_8_1_16', orm['core.SubmissionForm:study_plan_8_1_16']),
            ('study_plan_8_1_17', orm['core.SubmissionForm:study_plan_8_1_17']),
            ('study_plan_8_1_18', orm['core.SubmissionForm:study_plan_8_1_18']),
            ('study_plan_8_1_19', orm['core.SubmissionForm:study_plan_8_1_19']),
            ('study_plan_8_1_20', orm['core.SubmissionForm:study_plan_8_1_20']),
            ('study_plan_8_1_21', orm['core.SubmissionForm:study_plan_8_1_21']),
            ('study_plan_alpha', orm['core.SubmissionForm:study_plan_alpha']),
            ('study_plan_power', orm['core.SubmissionForm:study_plan_power']),
            ('study_plan_statalgorithm', orm['core.SubmissionForm:study_plan_statalgorithm']),
            ('study_plan_multiple_test_correction_algorithm', orm['core.SubmissionForm:study_plan_multiple_test_correction_algorithm']),
            ('study_plan_dropout_ratio', orm['core.SubmissionForm:study_plan_dropout_ratio']),
            ('study_plan_8_3_1', orm['core.SubmissionForm:study_plan_8_3_1']),
            ('study_plan_8_3_2', orm['core.SubmissionForm:study_plan_8_3_2']),
            ('study_plan_abort_crit', orm['core.SubmissionForm:study_plan_abort_crit']),
            ('study_plan_planned_statalgorithm', orm['core.SubmissionForm:study_plan_planned_statalgorithm']),
            ('study_plan_dataquality_checking', orm['core.SubmissionForm:study_plan_dataquality_checking']),
            ('study_plan_datamanagement', orm['core.SubmissionForm:study_plan_datamanagement']),
            ('study_plan_biometric_planning', orm['core.SubmissionForm:study_plan_biometric_planning']),
            ('study_plan_statistics_implementation', orm['core.SubmissionForm:study_plan_statistics_implementation']),
            ('study_plan_dataprotection_reason', orm['core.SubmissionForm:study_plan_dataprotection_reason']),
            ('study_plan_dataprotection_dvr', orm['core.SubmissionForm:study_plan_dataprotection_dvr']),
            ('study_plan_dataprotection_anonalgoritm', orm['core.SubmissionForm:study_plan_dataprotection_anonalgoritm']),
            ('submitter_name', orm['core.SubmissionForm:submitter_name']),
            ('submitter_organisation', orm['core.SubmissionForm:submitter_organisation']),
            ('submitter_jobtitle', orm['core.SubmissionForm:submitter_jobtitle']),
            ('submitter_is_coordinator', orm['core.SubmissionForm:submitter_is_coordinator']),
            ('submitter_is_main_investigator', orm['core.SubmissionForm:submitter_is_main_investigator']),
            ('submitter_is_sponsor', orm['core.SubmissionForm:submitter_is_sponsor']),
            ('submitter_is_authorized_by_sponsor', orm['core.SubmissionForm:submitter_is_authorized_by_sponsor']),
            ('submitter_sign_date', orm['core.SubmissionForm:submitter_sign_date']),
            ('investigator_name', orm['core.SubmissionForm:investigator_name']),
            ('investigator_organisation', orm['core.SubmissionForm:investigator_organisation']),
            ('investigator_phone', orm['core.SubmissionForm:investigator_phone']),
            ('investigator_mobile', orm['core.SubmissionForm:investigator_mobile']),
            ('investigator_fax', orm['core.SubmissionForm:investigator_fax']),
            ('investigator_email', orm['core.SubmissionForm:investigator_email']),
            ('investigator_jus_practicandi', orm['core.SubmissionForm:investigator_jus_practicandi']),
            ('investigator_specialist', orm['core.SubmissionForm:investigator_specialist']),
            ('investigator_certified', orm['core.SubmissionForm:investigator_certified']),
        ))
        db.send_create_signal('core', ['SubmissionForm'])
        
        # Adding model 'NotificationAnswer'
        db.create_table('core_notificationanswer', (
            ('id', orm['core.NotificationAnswer:id']),
            ('workflow', orm['core.NotificationAnswer:workflow']),
        ))
        db.send_create_signal('core', ['NotificationAnswer'])
        
        # Adding model 'Submission'
        db.create_table('core_submission', (
            ('id', orm['core.Submission:id']),
            ('submissionreview', orm['core.Submission:submissionreview']),
            ('vote', orm['core.Submission:vote']),
            ('workflow', orm['core.Submission:workflow']),
        ))
        db.send_create_signal('core', ['Submission'])
        
        # Adding model 'NotificationSet'
        db.create_table('core_notificationset', (
            ('id', orm['core.NotificationSet:id']),
            ('notificationform', orm['core.NotificationSet:notificationform']),
        ))
        db.send_create_signal('core', ['NotificationSet'])
        
        # Adding model 'SubmissionSet'
        db.create_table('core_submissionset', (
            ('id', orm['core.SubmissionSet:id']),
            ('submission', orm['core.SubmissionSet:submission']),
            ('submissionform', orm['core.SubmissionSet:submissionform']),
        ))
        db.send_create_signal('core', ['SubmissionSet'])
        
        # Adding model 'Meeting'
        db.create_table('core_meeting', (
            ('id', orm['core.Meeting:id']),
        ))
        db.send_create_signal('core', ['Meeting'])
        
        # Adding model 'InvolvedCommissionsForSubmission'
        db.create_table('core_involvedcommissionsforsubmission', (
            ('id', orm['core.InvolvedCommissionsForSubmission:id']),
            ('commission', orm['core.InvolvedCommissionsForSubmission:commission']),
            ('submission', orm['core.InvolvedCommissionsForSubmission:submission']),
            ('main', orm['core.InvolvedCommissionsForSubmission:main']),
        ))
        db.send_create_signal('core', ['InvolvedCommissionsForSubmission'])
        
        # Adding model 'Notification'
        db.create_table('core_notification', (
            ('id', orm['core.Notification:id']),
            ('submission', orm['core.Notification:submission']),
            ('notificationset', orm['core.Notification:notificationset']),
            ('answer', orm['core.Notification:answer']),
            ('workflow', orm['core.Notification:workflow']),
        ))
        db.send_create_signal('core', ['Notification'])
        
        # Adding model 'InvestigatorEmployee'
        db.create_table('core_investigatoremployee', (
            ('id', orm['core.InvestigatorEmployee:id']),
            ('submission', orm['core.InvestigatorEmployee:submission']),
            ('sex', orm['core.InvestigatorEmployee:sex']),
            ('title', orm['core.InvestigatorEmployee:title']),
            ('surname', orm['core.InvestigatorEmployee:surname']),
            ('firstname', orm['core.InvestigatorEmployee:firstname']),
            ('organisation', orm['core.InvestigatorEmployee:organisation']),
        ))
        db.send_create_signal('core', ['InvestigatorEmployee'])
        
        # Adding model 'NotificationForm'
        db.create_table('core_notificationform', (
            ('id', orm['core.NotificationForm:id']),
        ))
        db.send_create_signal('core', ['NotificationForm'])
        
        # Adding model 'ParticipatingCenter'
        db.create_table('core_participatingcenter', (
            ('id', orm['core.ParticipatingCenter:id']),
            ('submission', orm['core.ParticipatingCenter:submission']),
            ('name', orm['core.ParticipatingCenter:name']),
            ('address_1', orm['core.ParticipatingCenter:address_1']),
            ('address_2', orm['core.ParticipatingCenter:address_2']),
            ('zip_code', orm['core.ParticipatingCenter:zip_code']),
            ('city', orm['core.ParticipatingCenter:city']),
            ('country', orm['core.ParticipatingCenter:country']),
        ))
        db.send_create_signal('core', ['ParticipatingCenter'])
        
        # Adding model 'VoteReview'
        db.create_table('core_votereview', (
            ('id', orm['core.VoteReview:id']),
            ('workflow', orm['core.VoteReview:workflow']),
        ))
        db.send_create_signal('core', ['VoteReview'])
        
        # Adding ManyToManyField 'Vote.checklists'
        db.create_table('core_vote_checklists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vote', models.ForeignKey(orm.Vote, null=False)),
            ('checklist', models.ForeignKey(orm.Checklist, null=False))
        ))
        
        # Adding ManyToManyField 'NotificationSet.documents'
        db.create_table('core_notificationset_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notificationset', models.ForeignKey(orm.NotificationSet, null=False)),
            ('document', models.ForeignKey(orm.Document, null=False))
        ))
        
        # Adding ManyToManyField 'Meeting.submissions'
        db.create_table('core_meeting_submissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meeting', models.ForeignKey(orm.Meeting, null=False)),
            ('submission', models.ForeignKey(orm.Submission, null=False))
        ))
        
        # Adding ManyToManyField 'SubmissionSet.documents'
        db.create_table('core_submissionset_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submissionset', models.ForeignKey(orm.SubmissionSet, null=False)),
            ('document', models.ForeignKey(orm.Document, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Vote'
        db.delete_table('core_vote')
        
        # Deleting model 'DiagnosticsApplied'
        db.delete_table('core_diagnosticsapplied')
        
        # Deleting model 'SubmissionReview'
        db.delete_table('core_submissionreview')
        
        # Deleting model 'NonTestedUsedDrugs'
        db.delete_table('core_nontesteduseddrugs')
        
        # Deleting model 'EthicsCommission'
        db.delete_table('core_ethicscommission')
        
        # Deleting model 'Workflow'
        db.delete_table('core_workflow')
        
        # Deleting model 'Checklist'
        db.delete_table('core_checklist')
        
        # Deleting model 'Amendment'
        db.delete_table('core_amendment')
        
        # Deleting model 'Document'
        db.delete_table('core_document')
        
        # Deleting model 'TherapiesApplied'
        db.delete_table('core_therapiesapplied')
        
        # Deleting model 'Investigator'
        db.delete_table('core_investigator')
        
        # Deleting model 'SubmissionForm'
        db.delete_table('core_submissionform')
        
        # Deleting model 'NotificationAnswer'
        db.delete_table('core_notificationanswer')
        
        # Deleting model 'Submission'
        db.delete_table('core_submission')
        
        # Deleting model 'NotificationSet'
        db.delete_table('core_notificationset')
        
        # Deleting model 'SubmissionSet'
        db.delete_table('core_submissionset')
        
        # Deleting model 'Meeting'
        db.delete_table('core_meeting')
        
        # Deleting model 'InvolvedCommissionsForSubmission'
        db.delete_table('core_involvedcommissionsforsubmission')
        
        # Deleting model 'Notification'
        db.delete_table('core_notification')
        
        # Deleting model 'InvestigatorEmployee'
        db.delete_table('core_investigatoremployee')
        
        # Deleting model 'NotificationForm'
        db.delete_table('core_notificationform')
        
        # Deleting model 'ParticipatingCenter'
        db.delete_table('core_participatingcenter')
        
        # Deleting model 'VoteReview'
        db.delete_table('core_votereview')
        
        # Dropping ManyToManyField 'Vote.checklists'
        db.delete_table('core_vote_checklists')
        
        # Dropping ManyToManyField 'NotificationSet.documents'
        db.delete_table('core_notificationset_documents')
        
        # Dropping ManyToManyField 'Meeting.submissions'
        db.delete_table('core_meeting_submissions')
        
        # Dropping ManyToManyField 'SubmissionSet.documents'
        db.delete_table('core_submissionset_documents')
        
    
    
    models = {
        'core.amendment': {
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'submissionform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.checklist': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.diagnosticsapplied': {
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"}),
            'total': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'core.document': {
            'absent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid_document': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'uuid_document_revision': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'core.ethicscommission': {
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.investigator': {
            'certified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jus_practicandi': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'sign_date': ('django.db.models.fields.DateField', [], {}),
            'specialist': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.investigatoremployee': {
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Investigator']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'core.involvedcommissionsforsubmission': {
            'commission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.EthicsCommission']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.meeting': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Submission']"})
        },
        'core.nontesteduseddrugs': {
            'dosage': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'generic_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preparation_form': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.notification': {
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.NotificationAnswer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notificationset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.NotificationSet']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Submission']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.notificationanswer': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.notificationform': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.notificationset': {
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notificationform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.NotificationForm']"})
        },
        'core.participatingcenter': {
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.submission': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionreview': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionReview']"}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Vote']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.submissionform': {
            'additional_therapy_info': ('django.db.models.fields.TextField', [], {}),
            'already_voted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'clinical_phase': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'date_of_protocol': ('django.db.models.fields.DateField', [], {}),
            'eudract_number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'german_abort_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_additional_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_aftercare_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_benefits_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_concurrent_study_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_consent_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_dataaccess_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_dataprotection_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_ethical_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_financing_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_inclusion_exclusion_crit': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_payment_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_preclinical_results': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_primary_hypothesis': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_project_title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_protected_subjects_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_recruitment_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_relationship_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_risks_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_sideeffects_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_statistical_info': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'german_summary': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insurance_address_1': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'insurance_contract_number': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'insurance_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'insurance_phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'insurance_validity': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'investigator_certified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'investigator_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'investigator_fax': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'investigator_jus_practicandi': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'investigator_mobile': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'investigator_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'investigator_organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'investigator_phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'investigator_specialist': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'invoice_address1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'invoice_address2': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'invoice_city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'invoice_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'invoice_fax': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'invoice_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'invoice_phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'invoice_uid': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'invoice_uid_verified_level1': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'invoice_uid_verified_level2': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'invoice_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'isrctn_number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'medtech_ce_symbol': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'medtech_certified_for_exact_indications': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'medtech_certified_for_other_indications': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'medtech_checked_product': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'medtech_departure_from_regulations': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'medtech_manual_included': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'medtech_manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'medtech_product_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'medtech_reference_substance': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'medtech_technical_safety_regulations': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'pharma_checked_substance': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'pharma_reference_substance': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'project_title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'project_type_2_1_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_2_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_2_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_3': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_4': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_4_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_4_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_4_3': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_5': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_7': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_8': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_2_1_9': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'protocol_number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'specialism': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sponsor_address1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'sponsor_address2': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'sponsor_city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'sponsor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'sponsor_fax': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'sponsor_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sponsor_phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'sponsor_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'study_plan_8_1_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_10': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_11': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_12': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_13': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_14': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_15': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_16': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_17': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_18': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_19': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_20': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_21': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_8_1_3': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_4': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_5': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_7': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_8': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_9': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_3_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_3_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_abort_crit': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_alpha': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_biometric_planning': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_datamanagement': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dataprotection_anonalgoritm': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'study_plan_dataprotection_dvr': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'study_plan_dataprotection_reason': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_dataquality_checking': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dropout_ratio': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_multiple_test_correction_algorithm': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_planned_statalgorithm': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_power': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_statalgorithm': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_statistics_implementation': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
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
            'submitter_is_authorized_by_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_coordinator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_main_investigator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_sign_date': ('django.db.models.fields.DateField', [], {}),
            'substance_p_c_t_application_type': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'substance_p_c_t_countries': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'substance_p_c_t_final_report': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'substance_p_c_t_gcp_rules': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'substance_p_c_t_period': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'substance_p_c_t_phase': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'substance_preexisting_clinical_tries': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'substance_registered_in_countries': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'core.submissionreview': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.submissionset': {
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sets'", 'to': "orm['core.Submission']"}),
            'submissionform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.therapiesapplied': {
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"}),
            'total': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'core.vote': {
            'checklists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Checklist']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionSet']"}),
            'votereview': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.VoteReview']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.votereview': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.workflow': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['core']
