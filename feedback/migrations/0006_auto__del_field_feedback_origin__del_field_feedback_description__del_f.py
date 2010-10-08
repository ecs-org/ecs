# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Feedback.origin'
        db.delete_column('feedback_feedback', 'origin')

        # Deleting field 'Feedback.description'
        db.delete_column('feedback_feedback', 'description')

        # Deleting field 'Feedback.trac_ticket_id'
        db.delete_column('feedback_feedback', 'trac_ticket_id')

        # Deleting field 'Feedback.feedbacktype'
        db.delete_column('feedback_feedback', 'feedbacktype')

        # Deleting field 'Feedback.user'
        db.delete_column('feedback_feedback', 'user_id')

        # Deleting field 'Feedback.summary'
        db.delete_column('feedback_feedback', 'summary')

        # Deleting field 'Feedback.pub_date'
        db.delete_column('feedback_feedback', 'pub_date')

        # Removing M2M table for field me_too_votes on 'Feedback'
        db.delete_table('feedback_feedback_me_too_votes')


    def backwards(self, orm):
        
        # Adding field 'Feedback.origin'
        db.add_column('feedback_feedback', 'origin', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Feedback.description'
        db.add_column('feedback_feedback', 'description', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)

        # Adding field 'Feedback.trac_ticket_id'
        db.add_column('feedback_feedback', 'trac_ticket_id', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Feedback.feedbacktype'
        db.add_column('feedback_feedback', 'feedbacktype', self.gf('django.db.models.fields.CharField')(default='i', max_length=1), keep_default=False)

        # Adding field 'Feedback.user'
        db.add_column('feedback_feedback', 'user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='author', null=True, to=orm['auth.User']), keep_default=False)

        # Adding field 'Feedback.summary'
        db.add_column('feedback_feedback', 'summary', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Feedback.pub_date'
        db.add_column('feedback_feedback', 'pub_date', self.gf('django.db.models.fields.DateTimeField')(default=''), keep_default=False)

        # Adding M2M table for field me_too_votes on 'Feedback'
        db.create_table('feedback_feedback_me_too_votes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feedback', models.ForeignKey(orm['feedback.feedback'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('feedback_feedback_me_too_votes', ['feedback_id', 'user_id'])


    models = {
        'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['feedback']
