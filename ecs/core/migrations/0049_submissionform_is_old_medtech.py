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
        migrations.RunSQL('''
            UPDATE core_submissionform SET is_old_medtech = true WHERE project_type_medical_device = true;
            UPDATE core_submissionform SET is_old_medtech = false WHERE project_type_medical_device = true AND created_at >= '2022-07-01';
            UPDATE core_submissionform SET submission_type = 1 WHERE project_type_medical_device = true AND submission_type IS NULL;
        '''),
    ]
