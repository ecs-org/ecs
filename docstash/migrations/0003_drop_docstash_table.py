
from south.db import db
from django.db import models
from docstash.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Deleting model 'docstash'
        db.delete_table('docstash_docstash')
        
    
    
    def backwards(self, orm):
        
        # Adding model 'docstash'
        db.create_table('docstash_docstash', (
            ('modtime', orm['docstash.docstash:modtime']),
            ('name', orm['docstash.docstash:name']),
            ('form', orm['docstash.docstash:form']),
            ('value', orm['docstash.docstash:value']),
            ('token', orm['docstash.docstash:token']),
            ('key', orm['docstash.docstash:key']),
        ))
        db.send_create_signal('docstash', ['docstash'])
        
    
    
    models = {
        
    }
    
    complete_apps = ['docstash']
