# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'AssignedFastLaneCategory', fields ['meeting', 'category']
        db.delete_unique('fastlane_assignedfastlanecategory', ['meeting_id', 'category_id'])

        # Deleting model 'FastLaneMeeting'
        db.delete_table('fastlane_fastlanemeeting')

        # Deleting model 'AssignedFastLaneCategory'
        db.delete_table('fastlane_assignedfastlanecategory')

        # Deleting model 'FastLaneTop'
        db.delete_table('fastlane_fastlanetop')


    def backwards(self, orm):
        
        # Adding model 'FastLaneMeeting'
        db.create_table('fastlane_fastlanemeeting', (
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('started', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('ended', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('fastlane', ['FastLaneMeeting'])

        # Adding model 'AssignedFastLaneCategory'
        db.create_table('fastlane_assignedfastlanecategory', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_fastlane_categories', unique=True, to=orm['core.ExpeditedReviewCategory'])),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='categories', null=True, to=orm['fastlane.FastLaneMeeting'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_fastlane_categories', null=True, to=orm['auth.User'], blank=True)),
        ))
        db.send_create_signal('fastlane', ['AssignedFastLaneCategory'])

        # Adding unique constraint on 'AssignedFastLaneCategory', fields ['meeting', 'category']
        db.create_unique('fastlane_assignedfastlanecategory', ['meeting_id', 'category_id'])

        # Adding model 'FastLaneTop'
        db.create_table('fastlane_fastlanetop', (
            ('submission', self.gf('django.db.models.fields.related.OneToOneField')(related_name='fast_lane_top', unique=True, to=orm['core.Submission'])),
            ('recommendation_comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('recommendation', self.gf('django.db.models.fields.NullBooleanField')(default=None, null=True, blank=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tops', to=orm['fastlane.FastLaneMeeting'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('fastlane', ['FastLaneTop'])


    models = {
        
    }

    complete_apps = ['fastlane']
