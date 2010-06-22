# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Annotation'
        db.create_table('pdfviewer_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('layoutData', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('pdfviewer', ['Annotation'])


    def backwards(self, orm):
        
        # Deleting model 'Annotation'
        db.delete_table('pdfviewer_annotation')


    models = {
        'pdfviewer.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layoutData': ('django.db.models.fields.TextField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'})
        }
    }

    complete_apps = ['pdfviewer']
