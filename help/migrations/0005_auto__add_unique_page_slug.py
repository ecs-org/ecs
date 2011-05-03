# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'Page', fields ['slug']
        db.create_unique('help_page', ['slug'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Page', fields ['slug']
        db.delete_unique('help_page', ['slug'])


    models = {
        'help.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['help.Page']", 'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tracking.View']", 'null': 'True', 'blank': 'True'})
        },
        'help.page': {
            'Meta': {'unique_together': "(('view', 'anchor'),)", 'object_name': 'Page'},
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tracking.View']", 'null': 'True', 'blank': 'True'})
        },
        'tracking.view': {
            'Meta': {'object_name': 'View'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['help']
