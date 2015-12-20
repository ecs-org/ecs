# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_id', models.PositiveIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_at', models.DateTimeField(null=True)),
                ('closed_at', models.DateTimeField(null=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('accepted', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaskType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('is_delegatable', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(related_name='task_types', to='auth.Group', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
