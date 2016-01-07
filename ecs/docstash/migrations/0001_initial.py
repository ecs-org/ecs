from django.db import models, migrations
from django.conf import settings
import picklefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocStash',
            fields=[
                ('key', models.CharField(max_length=41, serialize=False, primary_key=True)),
                ('group', models.CharField(max_length=120, null=True, db_index=True)),
                ('current_version', models.IntegerField(default=-1)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocStashData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.IntegerField()),
                ('value', picklefield.fields.PickledObjectField(editable=False)),
                ('modtime', models.DateTimeField(auto_now_add=True)),
                ('name', models.TextField(blank=True)),
                ('stash', models.ForeignKey(related_name='data', to='docstash.DocStash')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='docstashdata',
            unique_together={('version', 'stash')},
        ),
        migrations.AlterUniqueTogether(
            name='docstash',
            unique_together={('group', 'owner', 'content_type', 'object_id')},
        ),
    ]
