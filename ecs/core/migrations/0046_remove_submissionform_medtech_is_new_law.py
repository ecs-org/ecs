# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_submissionform_medtech_is_new_law'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionform',
            name='medtech_is_new_law',
        ),
    ]
