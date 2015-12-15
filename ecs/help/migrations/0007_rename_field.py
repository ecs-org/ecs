# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('help_attachment', 'screenshot', 'is_screenshot')

    def backwards(self, orm):
        db.rename_column('help_attachment', 'is_screenshot', 'screenshot')

    models = {
        'help.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_screenshot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['help.Page']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tracking.View']", 'null': 'True', 'blank': 'True'})
        },
        'help.page': {
            'Meta': {'unique_together': "(('view', 'anchor'),)", 'object_name': 'Page'},
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review_status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20'}),
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
