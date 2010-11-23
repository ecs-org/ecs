# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'NodeType'
        db.create_table('workflow_nodetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='workflow_node_types', null=True, to=orm['contenttypes.ContentType'])),
            ('implementation', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('data_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
        ))
        db.send_create_signal('workflow', ['NodeType'])

        # Adding model 'Graph'
        db.create_table('workflow_graph', (
            ('nodetype_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['workflow.NodeType'], unique=True, primary_key=True)),
            ('auto_start', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('workflow', ['Graph'])

        # Adding model 'Guard'
        db.create_table('workflow_guard', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('implementation', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('workflow', ['Guard'])

        # Adding unique constraint on 'Guard', fields ['content_type', 'implementation']
        db.create_unique('workflow_guard', ['content_type_id', 'implementation'])

        # Adding model 'Node'
        db.create_table('workflow_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('graph', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nodes', to=orm['workflow.Graph'])),
            ('node_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workflow.NodeType'])),
            ('data_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('data_ct', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('is_start_node', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_end_node', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('workflow', ['Node'])

        # Adding model 'Edge'
        db.create_table('workflow_edge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='edges', null=True, to=orm['workflow.Node'])),
            ('to_node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='incoming_edges', null=True, to=orm['workflow.Node'])),
            ('deadline', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('guard', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nodes', null=True, to=orm['workflow.Guard'])),
            ('negated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('workflow', ['Edge'])

        # Adding model 'Workflow'
        db.create_table('workflow_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('data_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('graph', self.gf('django.db.models.fields.related.ForeignKey')(related_name='workflows', to=orm['workflow.Graph'])),
            ('is_finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parent_workflow', null=True, to=orm['workflow.Token'])),
        ))
        db.send_create_signal('workflow', ['Workflow'])

        # Adding model 'Token'
        db.create_table('workflow_token', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tokens', to=orm['workflow.Workflow'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tokens', to=orm['workflow.Node'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_tokens', null=True, to=orm['workflow.Node'])),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('consumed_at', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('consumed_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('workflow', ['Token'])

        # Adding M2M table for field trail on 'Token'
        db.create_table('workflow_token_trail', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_token', models.ForeignKey(orm['workflow.token'], null=False)),
            ('to_token', models.ForeignKey(orm['workflow.token'], null=False))
        ))
        db.create_unique('workflow_token_trail', ['from_token_id', 'to_token_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Guard', fields ['content_type', 'implementation']
        db.delete_unique('workflow_guard', ['content_type_id', 'implementation'])

        # Deleting model 'NodeType'
        db.delete_table('workflow_nodetype')

        # Deleting model 'Graph'
        db.delete_table('workflow_graph')

        # Deleting model 'Guard'
        db.delete_table('workflow_guard')

        # Deleting model 'Node'
        db.delete_table('workflow_node')

        # Deleting model 'Edge'
        db.delete_table('workflow_edge')

        # Deleting model 'Workflow'
        db.delete_table('workflow_workflow')

        # Deleting model 'Token'
        db.delete_table('workflow_token')

        # Removing M2M table for field trail on 'Token'
        db.delete_table('workflow_token_trail')


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
            'outputs': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'inputs'", 'symmetrical': 'False', 'through': "orm['workflow.Edge']", 'to': "orm['workflow.Node']"})
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
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_workflow'", 'null': 'True', 'to': "orm['workflow.Token']"})
        }
    }

    complete_apps = ['workflow']
