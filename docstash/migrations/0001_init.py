# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'DocStash'
        db.create_table('docstash_docstash', (
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('current_version', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, db_index=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=41, primary_key=True)),
        ))
        db.send_create_signal('docstash', ['DocStash'])

        # Adding model 'DocStashData'
        db.create_table('docstash_docstashdata', (
            ('modtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('value', self.gf('django_extensions.db.fields.json.JSONField')()),
            ('version', self.gf('django.db.models.fields.IntegerField')()),
            ('stash', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data', to=orm['docstash.DocStash'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('docstash', ['DocStashData'])

        # Adding unique constraint on 'DocStashData', fields ['version', 'stash']
        db.create_unique('docstash_docstashdata', ['version', 'stash_id'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'DocStash'
        db.delete_table('docstash_docstash')

        # Deleting model 'DocStashData'
        db.delete_table('docstash_docstashdata')

        # Removing unique constraint on 'DocStashData', fields ['version', 'stash']
        db.delete_unique('docstash_docstashdata', ['version', 'stash_id'])
    
    
    models = {
        'docstash.docstash': {
            'Meta': {'object_name': 'DocStash'},
            'current_version': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'db_index': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '41', 'primary_key': 'True'})
        },
        'docstash.docstashdata': {
            'Meta': {'unique_together': "(('version', 'stash'),)", 'object_name': 'DocStashData'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'stash': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': "orm['docstash.DocStash']"}),
            'value': ('django_extensions.db.fields.json.JSONField', [], {}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['docstash']
