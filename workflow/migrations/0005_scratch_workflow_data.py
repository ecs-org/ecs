# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    
    def forwards(self, orm):
        #orm.TaskType.objects.all().delete()
        #orm.Graph.objects.all().delete()
        pass
    
    def backwards(self, orm):
        "Write your backwards methods here."
    
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
            'Meta': {'unique_together': "(('content_type', 'implementation'),)", 'object_name': 'NodeType'},
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
    
    complete_apps = ['workflow']
