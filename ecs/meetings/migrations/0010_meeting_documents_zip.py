# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_uuidfield'),
        ('meetings', '0009_auto_20170106_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='documents_zip',
            field=models.ForeignKey(to='documents.Document', related_name='zip_for_meeting', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
