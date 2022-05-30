# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20170203_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionform',
            name='medtech_is_new_law',
            field=models.NullBooleanField(default=False),
        ),
    ]
