# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_djcelery'),
    ]

    operations = [
        migrations.RunSQL('''
            update core_submissionform
            set subject_maxage = 0
            where subject_maxage < 0;
        '''),
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
