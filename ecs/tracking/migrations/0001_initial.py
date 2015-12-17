# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip', models.IPAddressField(db_index=True)),
                ('url', models.TextField()),
                ('anchor', models.CharField(db_index=True, max_length=100, blank=True)),
                ('title', models.TextField(blank=True)),
                ('content_type', models.CharField(max_length=100)),
                ('method', models.CharField(db_index=True, max_length=4, choices=[(b'GET', b'GET'), (b'POST', b'POST')])),
                ('user', models.ForeignKey(related_name='requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=200, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='request',
            name='view',
            field=models.ForeignKey(to='tracking.View'),
            preserve_default=True,
        ),
    ]
