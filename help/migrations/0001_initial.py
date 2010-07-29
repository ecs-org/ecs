# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Page'
        db.create_table('help_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracking.View'], null=True, blank=True)),
            ('anchor', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('help', ['Page'])

        # Adding unique constraint on 'Page', fields ['view', 'anchor']
        db.create_unique('help_page', ['view_id', 'anchor'])

        # Adding model 'Attachment'
        db.create_table('help_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('help', ['Attachment'])


    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('help_page')

        # Removing unique constraint on 'Page', fields ['view', 'anchor']
        db.delete_unique('help_page', ['view_id', 'anchor'])

        # Deleting model 'Attachment'
        db.delete_table('help_attachment')


    models = {
        'help.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'help.page': {
            'Meta': {'unique_together': "(('view', 'anchor'),)", 'object_name': 'Page'},
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
