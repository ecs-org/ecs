
from south.db import db
from django.db import models
from docstash.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'DocStash.current_version'
        db.add_column('docstash_docstash', 'current_version', orm['docstash.docstash:current_version'])
        
        # Adding field 'DocStash.group'
        db.add_column('docstash_docstash', 'group', orm['docstash.docstash:group'])
        
        # Deleting field 'DocStash.form'
        db.delete_column('docstash_docstash', 'form')
        
        # Deleting field 'DocStash.version'
        db.delete_column('docstash_docstash', 'version')
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'DocStash.current_version'
        db.delete_column('docstash_docstash', 'current_version')
        
        # Deleting field 'DocStash.group'
        db.delete_column('docstash_docstash', 'group')
        
        # Adding field 'DocStash.form'
        db.add_column('docstash_docstash', 'form', orm['docstash.docstash:form'])
        
        # Adding field 'DocStash.version'
        db.add_column('docstash_docstash', 'version', orm['docstash.docstash:version'])
        
    
    
    models = {
        'docstash.docstash': {
            'current_version': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'db_index': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '41', 'primary_key': 'True'})
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
