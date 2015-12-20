# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ecs.help.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(storage=ecs.help.models.AttachmentFileStorage(), upload_to=ecs.help.models.upload_to)),
                ('mimetype', models.CharField(max_length=100)),
                ('is_screenshot', models.BooleanField(default=False)),
                ('slug', models.CharField(unique=True, max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anchor', models.CharField(max_length=100, blank=True)),
                ('slug', models.CharField(unique=True, max_length=100)),
                ('title', models.CharField(max_length=150)),
                ('text', models.TextField()),
                ('review_status', models.CharField(default=b'new', max_length=20, choices=[(b'new', 'New'), (b'ready_for_review', 'Ready for Review'), (b'review_ok', 'Review OK'), (b'review_fail', 'Review Failed')])),
                ('view', models.ForeignKey(blank=True, to='tracking.View', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('view', 'anchor')]),
        ),
        migrations.AddField(
            model_name='attachment',
            name='page',
            field=models.ForeignKey(blank=True, to='help.Page', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attachment',
            name='view',
            field=models.ForeignKey(blank=True, to='tracking.View', null=True),
            preserve_default=True,
        ),
    ]
