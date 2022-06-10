# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_submissionform_medtech_is_new_law'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalcategory',
            name='is_disabled',
            field=models.BooleanField(default=False),
        ),
    ]
