# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'UserProfile.title'
        db.add_column('users_userprofile', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True), keep_default=False)

        # Adding field 'UserProfile.organisation'
        db.add_column('users_userprofile', 'organisation', self.gf('django.db.models.fields.CharField')(default='', max_length=180, blank=True), keep_default=False)

        # Adding field 'UserProfile.jobtitle'
        db.add_column('users_userprofile', 'jobtitle', self.gf('django.db.models.fields.CharField')(default='', max_length=130, blank=True), keep_default=False)

        # Adding field 'UserProfile.swift_bic'
        db.add_column('users_userprofile', 'swift_bic', self.gf('django.db.models.fields.CharField')(default='', max_length=11, blank=True), keep_default=False)

        # Adding field 'UserProfile.iban'
        db.add_column('users_userprofile', 'iban', self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'UserProfile.title'
        db.delete_column('users_userprofile', 'title')

        # Deleting field 'UserProfile.organisation'
        db.delete_column('users_userprofile', 'organisation')

        # Deleting field 'UserProfile.jobtitle'
        db.delete_column('users_userprofile', 'jobtitle')

        # Deleting field 'UserProfile.swift_bic'
        db.delete_column('users_userprofile', 'swift_bic')

        # Deleting field 'UserProfile.iban'
        db.delete_column('users_userprofile', 'iban')


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
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'approved_by_office': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'board_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'executive_board_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expedited_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'external_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indisposed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'insurance_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'internal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '130', 'blank': 'True'}),
            'last_password_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'single_login_enforced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'swift_bic': ('django.db.models.fields.CharField', [], {'max_length': '11', 'blank': 'True'}),
            'thesis_review': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ecs_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'users.usersettings': {
            'Meta': {'object_name': 'UserSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission_filter': ('django_extensions.db.fields.json.JSONField', [], {}),
            'task_filter': ('django_extensions.db.fields.json.JSONField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ecs_settings'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['users']
