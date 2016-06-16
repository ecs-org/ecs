# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_merge'),
        ('tasks', '0004_auto_20160308_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='medical_category',
            field=models.ForeignKey(null=True, to='core.MedicalCategory'),
        ),
        migrations.RunSQL('''
            update tasks_task
            set medical_category_id = (
                select medicalcategory_id
                from tasks_task_medical_categories
                where task_id = tasks_task.id
            )
        '''),
        migrations.RemoveField(
            model_name='task',
            name='medical_categories',
        ),
    ]
