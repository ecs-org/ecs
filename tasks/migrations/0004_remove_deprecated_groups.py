# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        groups = orm['auth.Group'].objects.filter(name__in=[u'Presenter', u'Sponsor', u'Investigator'])
        task_types = orm['tasks.TaskType'].objects.all()

        for task_type in task_types:
            for group in groups:
                if group in task_type.groups.all():
                    task_type.groups.remove(group)
                    task_type.save()

    def backwards(self, orm):
        raise NotImplementedError


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'assigned_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'data_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['tasks.TaskType']"}),
            'workflow_token': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'task'", 'unique': 'True', 'null': 'True', 'to': "orm['workflow.Token']"})
        },
        'tasks.tasktype': {
            'Meta': {'object_name': 'TaskType'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'task_types'", 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'workflow_node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['workflow.Node']", 'unique': 'True', 'null': 'True'})
        },
        'workflow.edge': {
            'Meta': {'object_name': 'Edge'},
            'deadline': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'from_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'edges'", 'null': 'True', 'to': "orm['workflow.Node']"}),
            'guard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'null': 'True', 'to': "orm['workflow.Guard']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'negated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'to_node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_edges'", 'null': 'True', 'to': "orm['workflow.Node']"})
        },
        'workflow.graph': {
            'Meta': {'object_name': 'Graph', '_ormbases': ['workflow.NodeType']},
            'auto_start': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_end_node': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_start_node': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'node_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workflow.NodeType']"}),
            'outputs': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'inputs'", 'symmetrical': 'False', 'through': "orm['workflow.Edge']", 'to': "orm['workflow.Node']"}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tokens'", 'to': "orm['workflow.Node']"}),
            'repeated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_workflow'", 'null': 'True', 'to': "orm['workflow.Token']"})
        }
    }

    complete_apps = ['tasks']
