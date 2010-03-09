
from south.db import db
from django.db import models
from docstash.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DocStash'
        db.create_table('docstash_docstash', (
            ('key', orm['docstash.DocStash:key']),
            ('token', orm['docstash.DocStash:token']),
            ('value', orm['docstash.DocStash:value']),
            ('form', orm['docstash.DocStash:form']),
            ('name', orm['docstash.DocStash:name']),
        ))
        db.send_create_signal('docstash', ['DocStash'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DocStash'
        db.delete_table('docstash_docstash')
        
    
    
    models = {
        'docstash.docstash': {
            'form': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '41'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'token': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['docstash']
