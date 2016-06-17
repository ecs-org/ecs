# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('tasks', '0005_task_medical_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasktype',
            name='group',
            field=models.ForeignKey(null=True, related_name='task_types', to='auth.Group'),
        ),
        migrations.RunSQL('''
            update tasks_tasktype
            set group_id = (
                select group_id
                from tasks_tasktype_groups
                where tasktype_id = tasks_tasktype.id
            )
        '''),
        migrations.RemoveField(
            model_name='tasktype',
            name='groups',
        ),
    ]
