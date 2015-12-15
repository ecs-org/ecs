# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DocumentPersonalization'
        db.create_table('documents_documentpersonalization', (
            ('id', self.gf('django.db.models.fields.SlugField')(default='9d8bf99bdbff41d7a74ae23b0fc2d6ad', max_length=36, primary_key=True, db_index=True)),
            ('document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('documents', ['DocumentPersonalization'])

        # Adding model 'DocumentType'
        db.create_table('documents_documenttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('identifier', self.gf('django.db.models.fields.CharField')(default='', max_length=30, db_index=True, blank=True)),
            ('helptext', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('documents', ['DocumentType'])

        # Adding model 'Document'
        db.create_table('documents_document', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid_document', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=36, db_index=True)),
            ('hash', self.gf('django.db.models.fields.SlugField')(max_length=32, db_index=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=250, null=True)),
            ('original_file_name', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('doctype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.DocumentType'], null=True, blank=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(default='application/pdf', max_length=100)),
            ('pages', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('branding', self.gf('django.db.models.fields.CharField')(default='b', max_length=1)),
            ('allow_download', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('replaces_document', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'], null=True, blank=True)),
        ))
        db.send_create_signal('documents', ['Document'])

        # Adding model 'Page'
        db.create_table('documents_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('doc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['documents.Document'])),
            ('num', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('documents', ['Page'])


    def backwards(self, orm):
        
        # Deleting model 'DocumentPersonalization'
        db.delete_table('documents_documentpersonalization')

        # Deleting model 'DocumentType'
        db.delete_table('documents_documenttype')

        # Deleting model 'Document'
        db.delete_table('documents_document')

        # Deleting model 'Page'
        db.delete_table('documents_page')


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
        'documents.document': {
            'Meta': {'object_name': 'Document'},
            'allow_download': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'branding': ('django.db.models.fields.CharField', [], {'default': "'b'", 'max_length': '1'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.DocumentType']", 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250', 'null': 'True'}),
            'hash': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'application/pdf'", 'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'original_file_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'replaces_document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']", 'null': 'True', 'blank': 'True'}),
            'uuid_document': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '36', 'db_index': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'documents.documentpersonalization': {
            'Meta': {'object_name': 'DocumentPersonalization'},
            'document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']"}),
            'id': ('django.db.models.fields.SlugField', [], {'default': "'a2906e9bad9f44fbb06815f4cceb5bf5'", 'max_length': '36', 'primary_key': 'True', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'documents.documenttype': {
            'Meta': {'object_name': 'DocumentType'},
            'helptext': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'documents.page': {
            'Meta': {'object_name': 'Page'},
            'doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['documents']
