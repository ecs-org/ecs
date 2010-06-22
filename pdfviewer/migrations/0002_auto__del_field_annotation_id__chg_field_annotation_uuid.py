# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Annotation.id'
        db.delete_column('pdfviewer_annotation', 'id')

        # Changing field 'Annotation.uuid'
        db.alter_column('pdfviewer_annotation', 'uuid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True))


    def backwards(self, orm):
        
        # Adding field 'Annotation.id'
        db.add_column('pdfviewer_annotation', 'id', self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True), keep_default=False)

        # Changing field 'Annotation.uuid'
        db.alter_column('pdfviewer_annotation', 'uuid', self.gf('django.db.models.fields.CharField')(max_length=36, unique=True))


    models = {
        'pdfviewer.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'layoutData': ('django.db.models.fields.TextField', [], {}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        }
    }

    complete_apps = ['pdfviewer']
