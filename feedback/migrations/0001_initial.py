# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Feedback'
        db.create_table('feedback_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('feedback', ['Feedback'])


    def backwards(self, orm):
        
        # Deleting model 'Feedback'
        db.delete_table('feedback_feedback')


    models = {
        'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['feedback']
