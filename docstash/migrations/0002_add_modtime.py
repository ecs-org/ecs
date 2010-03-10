
from south.db import db
from django.db import models
from docstash.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'DocStash.modtime'
        db.add_column('docstash_docstash', 'modtime', orm['docstash.docstash:modtime'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'DocStash.modtime'
        db.delete_column('docstash_docstash', 'modtime')
        
    
    
    models = {
        'docstash.docstash': {
            'form': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '41'}),
            'modtime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'token': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['docstash']
