# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Message.origin'
        db.add_column('messages_message', 'origin', self.gf('django.db.models.fields.SmallIntegerField')(default=1), keep_default=False)

        # Changing field 'Message.thread'
        db.alter_column('messages_message', 'thread_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['messages.Thread']))
    
    
    def backwards(self, orm):
        
        # Deleting field 'Message.origin'
        db.delete_column('messages_message', 'origin')

        # Changing field 'Message.thread'
        db.alter_column('messages_message', 'thread_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['messages.Thread']))
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.expeditedreviewcategory': {
            'Meta': {'object_name': 'ExpeditedReviewCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'core.medicalcategory': {
            'Meta': {'object_name': 'MedicalCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'medical_categories'", 'to': "orm['auth.User']"})
        },
        'core.submission': {
            'Meta': {'object_name': 'Submission'},
            'additional_reviewers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'additional_review_submission_set'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'ec_number': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'expedited': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'expedited_review_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.ExpeditedReviewCategory']"}),
            'external_reviewer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'external_reviewer_name': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.MedicalCategory']"}),
            'retrospective': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'sponsor_required_for_next_meeting': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'thesis': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'})
        },
        'messages.message': {
            'Meta': {'object_name': 'Message'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_messages'", 'to': "orm['auth.User']"}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'replies'", 'null': 'True', 'to': "orm['messages.Message']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_messages'", 'to': "orm['auth.User']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['messages.Thread']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'unread': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'messages.thread': {
            'Meta': {'object_name': 'Thread'},
            'closed_by_receiver': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'closed_by_sender': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_threads'", 'to': "orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_threads'", 'to': "orm['auth.User']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Submission']", 'null': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']", 'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'assigned_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'data_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['tasks.TaskType']"}),
            'workflow_token': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['workflow.Token']", 'unique': 'True', 'null': 'True'})
        },
        'tasks.tasktype': {
            'Meta': {'object_name': 'TaskType'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'task_types'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'workflow_node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['workflow.Node']", 'unique': 'True', 'null': 'True'})
        },
        'workflow.edge': {
            'Meta': {'object_name': 'Edge'},
            'deadline': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'from_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'edges'", 'null': 'True', 'to': "orm['workflow.Node']"}),
            'guard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'null': 'True', 'to': "orm['workflow.Guard']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'negate': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'to_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_edges'", 'null': 'True', 'to': "orm['workflow.Node']"})
        },
        'workflow.graph': {
            'Meta': {'object_name': 'Graph', '_ormbases': ['workflow.NodeType']},
            'auto_start': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'nodetype_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['workflow.NodeType']", 'unique': 'True', 'primary_key': 'True'})
        },
        'workflow.guard': {
            'Meta': {'unique_together': "(('content_type', 'implementation'),)", 'object_name': 'Guard'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'workflow.node': {
            'Meta': {'object_name': 'Node'},
            'data_ct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'data_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'graph': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': "orm['workflow.Graph']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_end_node': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_start_node': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'node_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.NodeType']"}),
            'outputs': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'inputs'", 'symmetrical': 'False', 'through': "'Edge'", 'to': "orm['workflow.Node']"})
        },
        'workflow.nodetype': {
            'Meta': {'object_name': 'NodeType'},
            'category': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workflow_node_types'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'workflow.token': {
            'Meta': {'object_name': 'Token'},
            'consumed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'consumed_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tokens'", 'to': "orm['workflow.Node']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_tokens'", 'null': 'True', 'to': "orm['workflow.Node']"}),
            'trail': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'future'", 'symmetrical': 'False', 'to': "orm['workflow.Token']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tokens'", 'to': "orm['workflow.Workflow']"})
        },
        'workflow.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'data_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'graph': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workflows'", 'to': "orm['workflow.Graph']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_workflow'", 'null': 'True', 'to': "orm['workflow.Token']"})
        }
    }
    
    complete_apps = ['messages']
