# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_auto_20151217_1249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='expedited_review_categories',
            new_name='old_expedited_review_categories',
        ),
        migrations.AddField(
            model_name='task',
            name='expedited_review_categories',
            field=models.ManyToManyField(related_name='tasks_for_expedited_review', to='core.MedicalCategory'),
        ),
        migrations.RunSQL('''
            insert into tasks_task_expedited_review_categories (task_id, medicalcategory_id)
                select toerc.task_id, mc.id
                from tasks_task_old_expedited_review_categories toerc
                inner join core_expeditedreviewcategory erc
                    on erc.id = toerc.expeditedreviewcategory_id
                inner join core_medicalcategory mc on mc.abbrev = erc.abbrev
        '''),
        migrations.RemoveField(
            model_name='task',
            name='old_expedited_review_categories',
        ),
    ]
