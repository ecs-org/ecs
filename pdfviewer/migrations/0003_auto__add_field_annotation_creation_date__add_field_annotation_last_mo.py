# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Annotation.creation_date'
        db.add_column('pdfviewer_annotation', 'creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'Annotation.last_modified'
        db.add_column('pdfviewer_annotation', 'last_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Annotation.creation_date'
        db.delete_column('pdfviewer_annotation', 'creation_date')

        # Deleting field 'Annotation.last_modified'
        db.delete_column('pdfviewer_annotation', 'last_modified')


    models = {
        'pdfviewer.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'layoutData': ('django.db.models.fields.TextField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        }
    }

    complete_apps = ['pdfviewer']
