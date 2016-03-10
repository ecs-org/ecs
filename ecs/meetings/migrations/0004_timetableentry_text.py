# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0003_durationfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetableentry',
            name='text',
            field=models.TextField(null=True, blank=True),
        ),
    ]
