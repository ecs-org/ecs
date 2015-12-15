# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'UserProfile.external_review'
        db.delete_column('users_userprofile', 'external_review')


    def backwards(self, orm):
        
        # Adding field 'UserProfile.external_review'
        db.add_column('users_userprofile', 'external_review', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'users.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ecs_invitations'", 'to': "orm['auth.User']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'c8962b11df5f49c39e8fdb1d836a58d0'", 'unique': 'True', 'max_length': '32'})
        },
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'approved_by_office': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'board_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'executive_board_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expedited_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '45', 'blank': 'True'}),
            'forward_messages_after_minutes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'help_writer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indisposed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'insurance_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'internal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'last_password_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'phantom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'single_login_enforced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'social_security_number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'start_workflow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'swift_bic': ('django.db.models.fields.CharField', [], {'max_length': '11', 'blank': 'True'}),
            'thesis_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ecs_profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'users.usersettings': {
            'Meta': {'object_name': 'UserSettings'},
            'communication_filter': ('django_extensions.db.fields.json.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pdfviewer_settings': ('django_extensions.db.fields.json.JSONField', [], {}),
            'submission_filter_all': ('django_extensions.db.fields.json.JSONField', [], {}),
            'submission_filter_assigned': ('django_extensions.db.fields.json.JSONField', [], {}),
            'submission_filter_mine': ('django_extensions.db.fields.json.JSONField', [], {}),
            'submission_filter_search': ('django_extensions.db.fields.json.JSONField', [], {}),
            'submission_filter_widget': ('django_extensions.db.fields.json.JSONField', [], {}),
            'submission_filter_widget_internal': ('django_extensions.db.fields.json.JSONField', [], {}),
            'task_filter': ('django_extensions.db.fields.json.JSONField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ecs_settings'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'useradministration_filter': ('django_extensions.db.fields.json.JSONField', [], {})
        }
    }

    complete_apps = ['users']
