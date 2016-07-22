# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_cleanup_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='is_insurance_reviewer',
        ),
    ]
