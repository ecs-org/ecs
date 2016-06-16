# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def remove_non_repeatable_checklist_review_nt(apps, schema_editor):
    NodeType = apps.get_model('workflow', 'NodeType')
    try:
        nt = NodeType.objects.get(
            implementation='ecs.core.workflow.NonRepeatableChecklistReview')
    except NodeType.DoesNotExist:
        pass
    else:
        assert not nt.node_set.exists()
        nt.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_merge'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_non_repeatable_checklist_review_nt),
    ]
