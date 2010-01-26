# -*- coding: utf-8 -*- 

from south.db import db
from django.db import models
from core.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
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
