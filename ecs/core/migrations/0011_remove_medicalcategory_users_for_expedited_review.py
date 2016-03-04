# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_merge_medical_categories'),
    ]

    operations = [
        migrations.RunSQL('''
            insert into core_medicalcategory_users (medicalcategory_id, user_id)
                select medicalcategory_id, user_id
                from core_medicalcategory_users_for_expedited_review
                except
                select medicalcategory_id, user_id
                from core_medicalcategory_users;
        '''),
        migrations.RemoveField(
            model_name='medicalcategory',
            name='users_for_expedited_review',
        ),
    ]
