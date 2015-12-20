# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.SlugField(unique=True, max_length=36)),
                ('original_file_name', models.CharField(max_length=250, null=True, blank=True)),
                ('mimetype', models.CharField(default=b'application/pdf', max_length=100)),
                ('stamp_on_download', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=250)),
                ('version', models.CharField(max_length=250)),
                ('date', models.DateTimeField()),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('identifier', models.CharField(default=b'', max_length=30, db_index=True, blank=True)),
                ('helptext', models.TextField(default=b'', blank=True)),
                ('is_hidden', models.BooleanField(default=False)),
                ('is_downloadable', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DownloadHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('uuid', models.SlugField(max_length=36)),
                ('context', models.CharField(max_length=15)),
                ('document', models.ForeignKey(to='documents.Document')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['downloaded_at'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='document',
            name='doctype',
            field=models.ForeignKey(to='documents.DocumentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='document',
            name='replaces_document',
            field=models.ForeignKey(blank=True, to='documents.Document', null=True),
            preserve_default=True,
        ),
    ]
