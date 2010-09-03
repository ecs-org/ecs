# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ('core', '0028_move_documents'),
    )

    def forwards(self, orm):
        db.rename_table('core_assignedmedicalcategory', 'meetings_assignedmedicalcategory')
        db.rename_table('core_meeting', 'meetings_meeting')
        db.rename_table('core_timetableentry', 'meetings_timetableentry')
        db.rename_table('core_participation', 'meetings_participation')
        db.rename_table('core_constraint', 'meetings_constraint')

    def backwards(self, orm):
        db.rename_table('meetings_assignedmedicalcategory', 'core_assignedmedicalcategory')
        db.rename_table('meetings_meeting', 'core_meeting')
        db.rename_table('meetings_timetableentry', 'core_timetableentry')
        db.rename_table('meetings_participation', 'core_participation')
        db.rename_table('meetings_constraint', 'core_constraint')


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
        'core.expeditedreviewcategory': {
            'Meta': {'object_name': 'ExpeditedReviewCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'core.medicalcategory': {
            'Meta': {'object_name': 'MedicalCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'medical_categories'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'core.submission': {
            'Meta': {'object_name': 'Submission'},
            'additional_reviewers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'additional_review_submission_set'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'befangene': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'befangen_for_submissions'", 'null': 'True', 'to': "orm['auth.User']"}),
            'billed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'ec_number': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'expedited': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'expedited_review_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.ExpeditedReviewCategory']"}),
            'external_reviewer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'external_reviewer_billed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'external_reviewer_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reviewed_submissions'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_amg': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_mpg': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medical_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.MedicalCategory']"}),
            'remission': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'retrospective': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'sponsor_required_for_next_meeting': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'thesis': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'meetings.assignedmedicalcategory': {
            'Meta': {'unique_together': "(('category', 'meeting'),)", 'object_name': 'AssignedMedicalCategory'},
            'board_member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MedicalCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'medical_categories'", 'to': "orm['meetings.Meeting']"})
        },
        'meetings.constraint': {
            'Meta': {'object_name': 'Constraint'},
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'constraints'", 'to': "orm['meetings.Meeting']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_constraints'", 'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.5'})
        },
        'meetings.meeting': {
            'Meta': {'object_name': 'Meeting'},
            'ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optimization_task_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'submissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'meetings'", 'symmetrical': 'False', 'through': "orm['meetings.TimetableEntry']", 'to': "orm['core.Submission']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'meetings.participation': {
            'Meta': {'object_name': 'Participation'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participations'", 'to': "orm['meetings.TimetableEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meeting_participations'", 'null': 'True', 'to': "orm['core.MedicalCategory']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_participations'", 'to': "orm['auth.User']"})
        },
        'meetings.timetableentry': {
            'Meta': {'object_name': 'TimetableEntry'},
            'duration_in_seconds': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_break': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'timetable_entries'", 'to': "orm['meetings.Meeting']"}),
            'optimal_start': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'sponsor_invited': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'timetable_entries'", 'null': 'True', 'to': "orm['core.Submission']"}),
            'timetable_index': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['meetings']
