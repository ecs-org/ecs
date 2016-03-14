# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_djcelery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigator',
            name='subject_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='subject_count',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='subject_maxage',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='subject_minage',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
