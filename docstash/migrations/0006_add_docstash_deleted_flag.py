
from south.db import db
from django.db import models
from docstash.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'DocStash.deleted'
        db.add_column('docstash_docstash', 'deleted', orm['docstash.docstash:deleted'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'DocStash.deleted'
        db.delete_column('docstash_docstash', 'deleted')
        
    
    
    models = {
        'docstash.docstash': {
            'current_version': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
