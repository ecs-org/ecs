# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_uuidfield'),
        ('meetings', '0008_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='protocol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='protocol_for_meeting', to='documents.Document'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='protocol_rendering_started_at',
            field=models.DateTimeField(null=True),
        ),
    ]
