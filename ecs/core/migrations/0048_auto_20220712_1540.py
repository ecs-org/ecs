# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_remove_submissionform_medtech_is_new_law'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionform',
            name='submission_type',
            field=models.SmallIntegerField(choices=[(1, 'monocentric'), (2, 'multicentric, main ethics commission'), (6, 'multicentric, local ethics commission')], null=True, blank=True),
        ),
    ]
