# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_medicalcategory_users_for_expedited_review'),
    ]

    operations = [
        migrations.RunSQL('''
            insert into core_submission_medical_categories (medicalcategory_id, submission_id)
                select medicalcategory_id, submission_id
                from core_submission_expedited_review_categories
                except
                select medicalcategory_id, submission_id
                from core_submission_medical_categories
        '''),
        migrations.RemoveField(
            model_name='submission',
            name='expedited_review_categories',
        ),
    ]
