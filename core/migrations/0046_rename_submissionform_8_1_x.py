# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'SubmissionForm.study_plan_null_hypothesis'
        db.add_column('core_submissionform', 'study_plan_null_hypothesis', orm['core.submissionform:study_plan_null_hypothesis'])
        
        # Adding field 'SubmissionForm.study_plan_blind'
        db.add_column('core_submissionform', 'study_plan_blind', orm['core.submissionform:study_plan_blind'])
        
        # Adding field 'SubmissionForm.study_plan_equivalence_testing'
        db.add_column('core_submissionform', 'study_plan_equivalence_testing', orm['core.submissionform:study_plan_equivalence_testing'])
        
        # Adding field 'SubmissionForm.study_plan_placebo'
        db.add_column('core_submissionform', 'study_plan_placebo', orm['core.submissionform:study_plan_placebo'])
        
        # Adding field 'SubmissionForm.study_plan_number_of_groups'
        db.add_column('core_submissionform', 'study_plan_number_of_groups', orm['core.submissionform:study_plan_number_of_groups'])
        
        # Adding field 'SubmissionForm.study_plan_parallelgroups'
        db.add_column('core_submissionform', 'study_plan_parallelgroups', orm['core.submissionform:study_plan_parallelgroups'])
        
        # Adding field 'SubmissionForm.study_plan_sample_frequency'
        db.add_column('core_submissionform', 'study_plan_sample_frequency', orm['core.submissionform:study_plan_sample_frequency'])
        
        # Adding field 'SubmissionForm.study_plan_misc'
        db.add_column('core_submissionform', 'study_plan_misc', orm['core.submissionform:study_plan_misc'])
        
        # Adding field 'SubmissionForm.study_plan_cross_over'
        db.add_column('core_submissionform', 'study_plan_cross_over', orm['core.submissionform:study_plan_cross_over'])
        
        # Adding field 'SubmissionForm.study_plan_factorized'
        db.add_column('core_submissionform', 'study_plan_factorized', orm['core.submissionform:study_plan_factorized'])
        
        # Adding field 'SubmissionForm.study_plan_secondary_objectives'
        db.add_column('core_submissionform', 'study_plan_secondary_objectives', orm['core.submissionform:study_plan_secondary_objectives'])
        
        # Adding field 'SubmissionForm.study_plan_controlled'
        db.add_column('core_submissionform', 'study_plan_controlled', orm['core.submissionform:study_plan_controlled'])
        
        # Adding field 'SubmissionForm.study_plan_observer_blinded'
        db.add_column('core_submissionform', 'study_plan_observer_blinded', orm['core.submissionform:study_plan_observer_blinded'])
        
        # Adding field 'SubmissionForm.study_plan_pilot_project'
        db.add_column('core_submissionform', 'study_plan_pilot_project', orm['core.submissionform:study_plan_pilot_project'])
        
        # Adding field 'SubmissionForm.study_plan_alternative_hypothesis'
        db.add_column('core_submissionform', 'study_plan_alternative_hypothesis', orm['core.submissionform:study_plan_alternative_hypothesis'])
        
        # Adding field 'SubmissionForm.study_plan_stratification'
        db.add_column('core_submissionform', 'study_plan_stratification', orm['core.submissionform:study_plan_stratification'])
        
        # Adding field 'SubmissionForm.study_plan_randomized'
        db.add_column('core_submissionform', 'study_plan_randomized', orm['core.submissionform:study_plan_randomized'])
        
        # Adding field 'SubmissionForm.study_plan_primary_objectives'
        db.add_column('core_submissionform', 'study_plan_primary_objectives', orm['core.submissionform:study_plan_primary_objectives'])
        
        # Deleting field 'SubmissionForm.study_plan_8_1_19'
        db.delete_column('core_submissionform', 'study_plan_8_1_19')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_14'
        db.delete_column('core_submissionform', 'study_plan_8_1_14')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_15'
        db.delete_column('core_submissionform', 'study_plan_8_1_15')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_16'
        db.delete_column('core_submissionform', 'study_plan_8_1_16')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_5'
        db.delete_column('core_submissionform', 'study_plan_8_1_5')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_21'
        db.delete_column('core_submissionform', 'study_plan_8_1_21')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_17'
        db.delete_column('core_submissionform', 'study_plan_8_1_17')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_6'
        db.delete_column('core_submissionform', 'study_plan_8_1_6')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_20'
        db.delete_column('core_submissionform', 'study_plan_8_1_20')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_7'
        db.delete_column('core_submissionform', 'study_plan_8_1_7')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_22'
        db.delete_column('core_submissionform', 'study_plan_8_1_22')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_1'
        db.delete_column('core_submissionform', 'study_plan_8_1_1')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_10'
        db.delete_column('core_submissionform', 'study_plan_8_1_10')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_2'
        db.delete_column('core_submissionform', 'study_plan_8_1_2')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_11'
        db.delete_column('core_submissionform', 'study_plan_8_1_11')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_3'
        db.delete_column('core_submissionform', 'study_plan_8_1_3')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_12'
        db.delete_column('core_submissionform', 'study_plan_8_1_12')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_9'
        db.delete_column('core_submissionform', 'study_plan_8_1_9')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_18'
        db.delete_column('core_submissionform', 'study_plan_8_1_18')
        
        # Deleting field 'SubmissionForm.study_plan_8_1_13'
        db.delete_column('core_submissionform', 'study_plan_8_1_13')
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'SubmissionForm.study_plan_null_hypothesis'
        db.delete_column('core_submissionform', 'study_plan_null_hypothesis')
        
        # Deleting field 'SubmissionForm.study_plan_blind'
        db.delete_column('core_submissionform', 'study_plan_blind')
        
        # Deleting field 'SubmissionForm.study_plan_equivalence_testing'
        db.delete_column('core_submissionform', 'study_plan_equivalence_testing')
        
        # Deleting field 'SubmissionForm.study_plan_placebo'
        db.delete_column('core_submissionform', 'study_plan_placebo')
        
        # Deleting field 'SubmissionForm.study_plan_number_of_groups'
        db.delete_column('core_submissionform', 'study_plan_number_of_groups')
        
        # Deleting field 'SubmissionForm.study_plan_parallelgroups'
        db.delete_column('core_submissionform', 'study_plan_parallelgroups')
        
        # Deleting field 'SubmissionForm.study_plan_sample_frequency'
        db.delete_column('core_submissionform', 'study_plan_sample_frequency')
        
        # Deleting field 'SubmissionForm.study_plan_misc'
        db.delete_column('core_submissionform', 'study_plan_misc')
        
        # Deleting field 'SubmissionForm.study_plan_cross_over'
        db.delete_column('core_submissionform', 'study_plan_cross_over')
        
        # Deleting field 'SubmissionForm.study_plan_factorized'
        db.delete_column('core_submissionform', 'study_plan_factorized')
        
        # Deleting field 'SubmissionForm.study_plan_secondary_objectives'
        db.delete_column('core_submissionform', 'study_plan_secondary_objectives')
        
        # Deleting field 'SubmissionForm.study_plan_controlled'
        db.delete_column('core_submissionform', 'study_plan_controlled')
        
        # Deleting field 'SubmissionForm.study_plan_observer_blinded'
        db.delete_column('core_submissionform', 'study_plan_observer_blinded')
        
        # Deleting field 'SubmissionForm.study_plan_pilot_project'
        db.delete_column('core_submissionform', 'study_plan_pilot_project')
        
        # Deleting field 'SubmissionForm.study_plan_alternative_hypothesis'
        db.delete_column('core_submissionform', 'study_plan_alternative_hypothesis')
        
        # Deleting field 'SubmissionForm.study_plan_stratification'
        db.delete_column('core_submissionform', 'study_plan_stratification')
        
        # Deleting field 'SubmissionForm.study_plan_randomized'
        db.delete_column('core_submissionform', 'study_plan_randomized')
        
        # Deleting field 'SubmissionForm.study_plan_primary_objectives'
        db.delete_column('core_submissionform', 'study_plan_primary_objectives')
        
        # Adding field 'SubmissionForm.study_plan_8_1_19'
        db.add_column('core_submissionform', 'study_plan_8_1_19', orm['core.submissionform:study_plan_8_1_19'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_14'
        db.add_column('core_submissionform', 'study_plan_8_1_14', orm['core.submissionform:study_plan_8_1_14'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_15'
        db.add_column('core_submissionform', 'study_plan_8_1_15', orm['core.submissionform:study_plan_8_1_15'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_16'
        db.add_column('core_submissionform', 'study_plan_8_1_16', orm['core.submissionform:study_plan_8_1_16'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_5'
        db.add_column('core_submissionform', 'study_plan_8_1_5', orm['core.submissionform:study_plan_8_1_5'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_21'
        db.add_column('core_submissionform', 'study_plan_8_1_21', orm['core.submissionform:study_plan_8_1_21'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_17'
        db.add_column('core_submissionform', 'study_plan_8_1_17', orm['core.submissionform:study_plan_8_1_17'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_6'
        db.add_column('core_submissionform', 'study_plan_8_1_6', orm['core.submissionform:study_plan_8_1_6'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_20'
        db.add_column('core_submissionform', 'study_plan_8_1_20', orm['core.submissionform:study_plan_8_1_20'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_7'
        db.add_column('core_submissionform', 'study_plan_8_1_7', orm['core.submissionform:study_plan_8_1_7'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_22'
        db.add_column('core_submissionform', 'study_plan_8_1_22', orm['core.submissionform:study_plan_8_1_22'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_1'
        db.add_column('core_submissionform', 'study_plan_8_1_1', orm['core.submissionform:study_plan_8_1_1'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_10'
        db.add_column('core_submissionform', 'study_plan_8_1_10', orm['core.submissionform:study_plan_8_1_10'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_2'
        db.add_column('core_submissionform', 'study_plan_8_1_2', orm['core.submissionform:study_plan_8_1_2'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_11'
        db.add_column('core_submissionform', 'study_plan_8_1_11', orm['core.submissionform:study_plan_8_1_11'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_3'
        db.add_column('core_submissionform', 'study_plan_8_1_3', orm['core.submissionform:study_plan_8_1_3'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_12'
        db.add_column('core_submissionform', 'study_plan_8_1_12', orm['core.submissionform:study_plan_8_1_12'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_9'
        db.add_column('core_submissionform', 'study_plan_8_1_9', orm['core.submissionform:study_plan_8_1_9'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_18'
        db.add_column('core_submissionform', 'study_plan_8_1_18', orm['core.submissionform:study_plan_8_1_18'])
        
        # Adding field 'SubmissionForm.study_plan_8_1_13'
        db.add_column('core_submissionform', 'study_plan_8_1_13', orm['core.submissionform:study_plan_8_1_13'])
        
    
    
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
