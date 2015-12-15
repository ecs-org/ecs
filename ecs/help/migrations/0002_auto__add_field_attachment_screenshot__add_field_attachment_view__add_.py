# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Page', fields ['anchor', 'view']
        db.delete_unique('help_page', ['anchor', 'view_id'])

        # Adding field 'Attachment.screenshot'
        db.add_column('help_attachment', 'screenshot', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Attachment.view'
        db.add_column('help_attachment', 'view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracking.View'], null=True, blank=True), keep_default=False)

        # Adding field 'Attachment.page'
        db.add_column('help_attachment', 'page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['help.Page'], null=True, blank=True), keep_default=False)

        # Changing field 'Attachment.name'
        db.alter_column('help_attachment', 'name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Adding field 'Page.name'
        db.add_column('help_page', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Attachment.screenshot'
        db.delete_column('help_attachment', 'screenshot')

        # Deleting field 'Attachment.view'
        db.delete_column('help_attachment', 'view_id')

        # Deleting field 'Attachment.page'
        db.delete_column('help_attachment', 'page_id')

        # Changing field 'Attachment.name'
        db.alter_column('help_attachment', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Deleting field 'Page.name'
        db.delete_column('help_page', 'name')

        # Adding unique constraint on 'Page', fields ['anchor', 'view']
        db.create_unique('help_page', ['anchor', 'view_id'])


    models = {
        'help.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['help.Page']", 'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tracking.View']", 'null': 'True', 'blank': 'True'})
        },
        'help.page': {
            'Meta': {'object_name': 'Page'},
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
