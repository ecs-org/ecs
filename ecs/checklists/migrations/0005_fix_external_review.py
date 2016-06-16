# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def fix_external_review(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    TaskType = apps.get_model('tasks', 'TaskType')

    group = Group.objects.filter(name='External Reviewer').first()
    if group:
        TaskType.objects.filter(workflow_node__uid='external_review').update(
            group=group, is_delegatable=False)


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0004_remove_checklistblueprint_billing_required'),
        ('auth', '0006_require_contenttypes_0002'),
        ('tasks', '0006_task_type_group'),
    ]

    operations = [
        migrations.RunPython(fix_external_review),
    ]
