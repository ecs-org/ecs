# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_is_dynamic(apps, schema_editor):
    TaskType = apps.get_model('tasks', 'TaskType')
    TaskType.objects.filter(workflow_node__uid__in=(
        'board_member_review',
        'external_review',
        'gcp_review',
        'insurance_review',
        'legal_and_patient_review',
        'statistical_review',
    )).update(is_dynamic=True)


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_task_type_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasktype',
            name='is_dynamic',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_is_dynamic),
    ]
