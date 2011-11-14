# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Page.review_status'
        db.add_column('help_page', 'review_status', self.gf('django.db.models.fields.CharField')(default='new', max_length=20), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Page.review_status'
        db.delete_column('help_page', 'review_status')


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
