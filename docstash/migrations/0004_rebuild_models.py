
from south.db import db
from django.db import models
from docstash.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DocStashData'
        db.create_table('docstash_docstashdata', (
            ('id', orm['docstash.docstashdata:id']),
            ('version', orm['docstash.docstashdata:version']),
            ('stash', orm['docstash.docstashdata:stash']),
            ('value', orm['docstash.docstashdata:value']),
            ('modtime', orm['docstash.docstashdata:modtime']),
            ('name', orm['docstash.docstashdata:name']),
        ))
        db.send_create_signal('docstash', ['DocStashData'])
        
        # Adding model 'DocStash'
        db.create_table('docstash_docstash', (
            ('key', orm['docstash.docstash:key']),
            ('form', orm['docstash.docstash:form']),
            ('version', orm['docstash.docstash:version']),
        ))
        db.send_create_signal('docstash', ['DocStash'])
        
        # Creating unique_together for [version, stash] on DocStashData.
        db.create_unique('docstash_docstashdata', ['version', 'stash_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [version, stash] on DocStashData.
        db.delete_unique('docstash_docstashdata', ['version', 'stash_id'])
        
        # Deleting model 'DocStashData'
        db.delete_table('docstash_docstashdata')
        
        # Deleting model 'DocStash'
        db.delete_table('docstash_docstash')
        
    
    
    models = {
        'docstash.docstash': {
            'form': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '41', 'primary_key': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'docstash.docstashdata': {
            'Meta': {'unique_together': "(('version', 'stash'),)"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'stash': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': "orm['docstash.DocStash']"}),
            'value': ('JSONField', [], {}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        }
    }
    
    complete_apps = ['docstash']
