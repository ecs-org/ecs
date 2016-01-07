from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deadline', models.BooleanField(default=False)),
                ('negated', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Guard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('implementation', models.CharField(max_length=200)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('data_id', models.PositiveIntegerField(null=True)),
                ('is_start_node', models.BooleanField(default=False)),
                ('is_end_node', models.BooleanField(default=False)),
                ('uid', models.CharField(max_length=100, null=True)),
                ('data_ct', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('category', models.PositiveIntegerField(db_index=True, choices=[(1, 'activity'), (2, 'control'), (3, 'subgraph')])),
                ('implementation', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('nodetype_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='workflow.NodeType')),
                ('auto_start', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=('workflow.nodetype',),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deadline', models.DateTimeField(null=True)),
                ('locked', models.BooleanField(default=False)),
                ('repeated', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('consumed_at', models.DateTimeField(default=None, null=True, blank=True)),
                ('consumed_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('node', models.ForeignKey(related_name='tokens', to='workflow.Node')),
                ('source', models.ForeignKey(related_name='sent_tokens', to='workflow.Node', null=True)),
                ('trail', models.ManyToManyField(related_name='future', to='workflow.Token')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_id', models.PositiveIntegerField()),
                ('is_finished', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('graph', models.ForeignKey(related_name='workflows', to='workflow.Graph')),
                ('parent', models.ForeignKey(related_name='parent_workflow', to='workflow.Token', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='token',
            name='workflow',
            field=models.ForeignKey(related_name='tokens', to='workflow.Workflow'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nodetype',
            name='content_type',
            field=models.ForeignKey(related_name='workflow_node_types', to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nodetype',
            name='data_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='graph',
            field=models.ForeignKey(related_name='nodes', to='workflow.Graph'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='node_type',
            field=models.ForeignKey(to='workflow.NodeType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='outputs',
            field=models.ManyToManyField(related_name='inputs', through='workflow.Edge', to='workflow.Node'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='guard',
            unique_together={('content_type', 'implementation')},
        ),
        migrations.AddField(
            model_name='edge',
            name='from_node',
            field=models.ForeignKey(related_name='edges', to='workflow.Node', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='guard',
            field=models.ForeignKey(related_name='nodes', to='workflow.Guard', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='to_node',
            field=models.ForeignKey(related_name='incoming_edges', to='workflow.Node', null=True),
            preserve_default=True,
        ),
    ]
