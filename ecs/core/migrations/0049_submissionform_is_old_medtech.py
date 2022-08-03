# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_auto_20220712_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionform',
            name='is_old_medtech',
            field=models.NullBooleanField(),
        ),
    ]
