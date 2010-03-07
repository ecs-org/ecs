# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'SubmissionForm.project_type_non_reg_drug'
        db.add_column('core_submissionform', 'project_type_non_reg_drug', orm['core.submissionform:project_type_non_reg_drug'])
        
        # Adding field 'SubmissionForm.project_type_medical_device'
        db.add_column('core_submissionform', 'project_type_medical_device', orm['core.submissionform:project_type_medical_device'])
        
        # Adding field 'SubmissionForm.project_type_reg_drug_not_within_indication'
        db.add_column('core_submissionform', 'project_type_reg_drug_not_within_indication', orm['core.submissionform:project_type_reg_drug_not_within_indication'])
        
        # Adding field 'SubmissionForm.project_type_medical_device_performance_evaluation'
        db.add_column('core_submissionform', 'project_type_medical_device_performance_evaluation', orm['core.submissionform:project_type_medical_device_performance_evaluation'])
        
        # Adding field 'SubmissionForm.project_type_questionnaire'
        db.add_column('core_submissionform', 'project_type_questionnaire', orm['core.submissionform:project_type_questionnaire'])
        
        # Adding field 'SubmissionForm.project_type_misc'
        db.add_column('core_submissionform', 'project_type_misc', orm['core.submissionform:project_type_misc'])
        
        # Adding field 'SubmissionForm.project_type_education_context'
        db.add_column('core_submissionform', 'project_type_education_context', orm['core.submissionform:project_type_education_context'])
        
        # Adding field 'SubmissionForm.project_type_basic_research'
        db.add_column('core_submissionform', 'project_type_basic_research', orm['core.submissionform:project_type_basic_research'])
        
        # Adding field 'SubmissionForm.project_type_medical_method'
        db.add_column('core_submissionform', 'project_type_medical_method', orm['core.submissionform:project_type_medical_method'])
        
        # Adding field 'SubmissionForm.project_type_medical_device_without_ce'
        db.add_column('core_submissionform', 'project_type_medical_device_without_ce', orm['core.submissionform:project_type_medical_device_without_ce'])
        
        # Adding field 'SubmissionForm.project_type_medical_device_with_ce'
        db.add_column('core_submissionform', 'project_type_medical_device_with_ce', orm['core.submissionform:project_type_medical_device_with_ce'])
        
        # Adding field 'SubmissionForm.project_type_register'
        db.add_column('core_submissionform', 'project_type_register', orm['core.submissionform:project_type_register'])
        
        # Adding field 'SubmissionForm.project_type_reg_drug_within_indication'
        db.add_column('core_submissionform', 'project_type_reg_drug_within_indication', orm['core.submissionform:project_type_reg_drug_within_indication'])
        
        # Adding field 'SubmissionForm.project_type_retrospective'
        db.add_column('core_submissionform', 'project_type_retrospective', orm['core.submissionform:project_type_retrospective'])
        
        # Adding field 'SubmissionForm.project_type_reg_drug'
        db.add_column('core_submissionform', 'project_type_reg_drug', orm['core.submissionform:project_type_reg_drug'])
        
        # Adding field 'SubmissionForm.project_type_genetic_study'
        db.add_column('core_submissionform', 'project_type_genetic_study', orm['core.submissionform:project_type_genetic_study'])
        
        # Adding field 'SubmissionForm.project_type_biobank'
        db.add_column('core_submissionform', 'project_type_biobank', orm['core.submissionform:project_type_biobank'])
        
        # Deleting field 'SubmissionForm.project_type_2_1_4_2'
        db.delete_column('core_submissionform', 'project_type_2_1_4_2')
        
        # Deleting field 'SubmissionForm.project_type_2_1_3'
        db.delete_column('core_submissionform', 'project_type_2_1_3')
        
        # Deleting field 'SubmissionForm.project_type_2_1_4_3'
        db.delete_column('core_submissionform', 'project_type_2_1_4_3')
        
        # Deleting field 'SubmissionForm.project_type_2_1_2'
        db.delete_column('core_submissionform', 'project_type_2_1_2')
        
        # Deleting field 'SubmissionForm.project_type_2_1_5'
        db.delete_column('core_submissionform', 'project_type_2_1_5')
        
        # Deleting field 'SubmissionForm.project_type_2_1_4_1'
        db.delete_column('core_submissionform', 'project_type_2_1_4_1')
        
        # Deleting field 'SubmissionForm.project_type_2_1_4'
        db.delete_column('core_submissionform', 'project_type_2_1_4')
        
        # Deleting field 'SubmissionForm.project_type_2_1_7'
        db.delete_column('core_submissionform', 'project_type_2_1_7')
        
        # Deleting field 'SubmissionForm.project_type_2_1_6'
        db.delete_column('core_submissionform', 'project_type_2_1_6')
        
        # Deleting field 'SubmissionForm.project_type_2_1_2_1'
        db.delete_column('core_submissionform', 'project_type_2_1_2_1')
        
        # Deleting field 'SubmissionForm.project_type_2_1_9'
        db.delete_column('core_submissionform', 'project_type_2_1_9')
        
        # Deleting field 'SubmissionForm.project_type_2_1_2_2'
        db.delete_column('core_submissionform', 'project_type_2_1_2_2')
        
        # Deleting field 'SubmissionForm.project_type_2_1_8'
        db.delete_column('core_submissionform', 'project_type_2_1_8')
        
        # Deleting field 'SubmissionForm.project_type_2_1_1'
        db.delete_column('core_submissionform', 'project_type_2_1_1')
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'SubmissionForm.project_type_non_reg_drug'
        db.delete_column('core_submissionform', 'project_type_non_reg_drug')
        
        # Deleting field 'SubmissionForm.project_type_medical_device'
        db.delete_column('core_submissionform', 'project_type_medical_device')
        
        # Deleting field 'SubmissionForm.project_type_reg_drug_not_within_indication'
        db.delete_column('core_submissionform', 'project_type_reg_drug_not_within_indication')
        
        # Deleting field 'SubmissionForm.project_type_medical_device_performance_evaluation'
        db.delete_column('core_submissionform', 'project_type_medical_device_performance_evaluation')
        
        # Deleting field 'SubmissionForm.project_type_questionnaire'
        db.delete_column('core_submissionform', 'project_type_questionnaire')
        
        # Deleting field 'SubmissionForm.project_type_misc'
        db.delete_column('core_submissionform', 'project_type_misc')
        
        # Deleting field 'SubmissionForm.project_type_education_context'
        db.delete_column('core_submissionform', 'project_type_education_context')
        
        # Deleting field 'SubmissionForm.project_type_basic_research'
        db.delete_column('core_submissionform', 'project_type_basic_research')
        
        # Deleting field 'SubmissionForm.project_type_medical_method'
        db.delete_column('core_submissionform', 'project_type_medical_method')
        
        # Deleting field 'SubmissionForm.project_type_medical_device_without_ce'
        db.delete_column('core_submissionform', 'project_type_medical_device_without_ce')
        
        # Deleting field 'SubmissionForm.project_type_medical_device_with_ce'
        db.delete_column('core_submissionform', 'project_type_medical_device_with_ce')
        
        # Deleting field 'SubmissionForm.project_type_register'
        db.delete_column('core_submissionform', 'project_type_register')
        
        # Deleting field 'SubmissionForm.project_type_reg_drug_within_indication'
        db.delete_column('core_submissionform', 'project_type_reg_drug_within_indication')
        
        # Deleting field 'SubmissionForm.project_type_retrospective'
        db.delete_column('core_submissionform', 'project_type_retrospective')
        
        # Deleting field 'SubmissionForm.project_type_reg_drug'
        db.delete_column('core_submissionform', 'project_type_reg_drug')
        
        # Deleting field 'SubmissionForm.project_type_genetic_study'
        db.delete_column('core_submissionform', 'project_type_genetic_study')
        
        # Deleting field 'SubmissionForm.project_type_biobank'
        db.delete_column('core_submissionform', 'project_type_biobank')
        
        # Adding field 'SubmissionForm.project_type_2_1_4_2'
        db.add_column('core_submissionform', 'project_type_2_1_4_2', orm['core.submissionform:project_type_2_1_4_2'])
        
        # Adding field 'SubmissionForm.project_type_2_1_3'
        db.add_column('core_submissionform', 'project_type_2_1_3', orm['core.submissionform:project_type_2_1_3'])
        
        # Adding field 'SubmissionForm.project_type_2_1_4_3'
        db.add_column('core_submissionform', 'project_type_2_1_4_3', orm['core.submissionform:project_type_2_1_4_3'])
        
        # Adding field 'SubmissionForm.project_type_2_1_2'
        db.add_column('core_submissionform', 'project_type_2_1_2', orm['core.submissionform:project_type_2_1_2'])
        
        # Adding field 'SubmissionForm.project_type_2_1_5'
        db.add_column('core_submissionform', 'project_type_2_1_5', orm['core.submissionform:project_type_2_1_5'])
        
        # Adding field 'SubmissionForm.project_type_2_1_4_1'
        db.add_column('core_submissionform', 'project_type_2_1_4_1', orm['core.submissionform:project_type_2_1_4_1'])
        
        # Adding field 'SubmissionForm.project_type_2_1_4'
        db.add_column('core_submissionform', 'project_type_2_1_4', orm['core.submissionform:project_type_2_1_4'])
        
        # Adding field 'SubmissionForm.project_type_2_1_7'
        db.add_column('core_submissionform', 'project_type_2_1_7', orm['core.submissionform:project_type_2_1_7'])
        
        # Adding field 'SubmissionForm.project_type_2_1_6'
        db.add_column('core_submissionform', 'project_type_2_1_6', orm['core.submissionform:project_type_2_1_6'])
        
        # Adding field 'SubmissionForm.project_type_2_1_2_1'
        db.add_column('core_submissionform', 'project_type_2_1_2_1', orm['core.submissionform:project_type_2_1_2_1'])
        
        # Adding field 'SubmissionForm.project_type_2_1_9'
        db.add_column('core_submissionform', 'project_type_2_1_9', orm['core.submissionform:project_type_2_1_9'])
        
        # Adding field 'SubmissionForm.project_type_2_1_2_2'
        db.add_column('core_submissionform', 'project_type_2_1_2_2', orm['core.submissionform:project_type_2_1_2_2'])
        
        # Adding field 'SubmissionForm.project_type_2_1_8'
        db.add_column('core_submissionform', 'project_type_2_1_8', orm['core.submissionform:project_type_2_1_8'])
        
        # Adding field 'SubmissionForm.project_type_2_1_1'
        db.add_column('core_submissionform', 'project_type_2_1_1', orm['core.submissionform:project_type_2_1_1'])
        
    
    
    models = {
        'core.amendment': {
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'submissionform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']"})
        },
        'core.basenotificationform': {
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'direct_notifications'", 'null': 'True', 'to': "orm['core.Investigator']"}),
            'investigators': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Investigator']"}),
            'signed_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_forms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.SubmissionForm']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'null': 'True', 'to': "orm['core.NotificationType']"})
        },
        'core.checklist': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.document': {
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'doctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.DocumentType']", 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'application/pdf'", 'max_length': '100'}),
            'uuid_document': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'uuid_document_revision': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'core.documenttype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.ethicscommission': {
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'chairperson': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'contactname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.extendednotificationform': {
            'SAE_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'SUSAR_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'aborted_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'aborted_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'basenotificationform_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.BaseNotificationForm']", 'unique': 'True', 'primary_key': 'True'}),
            'extension_of_vote': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'finished_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'finished_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reason_for_not_started': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recruited_subjects': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'runs_till': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.investigator': {
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
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Investigator']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'core.measure': {
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'measures'", 'to': "orm['core.SubmissionForm']"}),
            'total': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
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
        'core.notificationanswer': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.notificationtype': {
            'form': ('django.db.models.fields.CharField', [], {'default': "'ecs.core.forms.BaseNotificationForm'", 'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'default': "'ecs.core.models.BaseNotificationForm'", 'max_length': '80'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
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
            'ec_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionreview': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionReview']", 'null': 'True'}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Vote']", 'null': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']", 'null': 'True'})
        },
        'core.submissionform': {
            'additional_therapy_info': ('django.db.models.fields.TextField', [], {}),
            'already_voted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'clinical_phase': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Document']"}),
            'ethics_commissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.EthicsCommission']"}),
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
            'project_title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'project_type_basic_research': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_biobank': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'project_type_education_context': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
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
            'study_plan_8_1_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_10': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_11': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_12': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_13': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_14': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_15': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_16': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_17': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_18': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_19': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_20': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_21': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_22': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'study_plan_8_1_3': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_5': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_6': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_7': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_1_9': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_3_1': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_8_3_2': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'study_plan_abort_crit': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_alpha': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'study_plan_biometric_planning': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'study_plan_datamanagement': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dataprotection_anonalgoritm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_dataprotection_dvr': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'study_plan_dataprotection_reason': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
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
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forms'", 'to': "orm['core.Submission']"}),
            'submitter_agrees_to_publishing': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'submitter_is_authorized_by_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_coordinator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_main_investigator': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_is_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submitter_jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_organisation': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'submitter_sign_date': ('django.db.models.fields.DateField', [], {}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Workflow']"})
        },
        'core.vote': {
            'checklists': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Checklist']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submissionform': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.SubmissionForm']", 'null': 'True'}),
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
