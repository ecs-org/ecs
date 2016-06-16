# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_workflow_graphs(apps, schema_editor):
    Guard = apps.get_model('workflow', 'Guard')
    Edge = apps.get_model('workflow', 'Edge')
    impls = (
        'ecs.core.workflow.needs_insurance_review',
        'ecs.core.workflow.needs_statistical_review',
        'ecs.core.workflow.needs_legal_and_patient_review',
        'ecs.core.workflow.needs_gcp_review',
    )
    guards = Guard.objects.filter(implementation__in=impls)
    Edge.objects.filter(guard__in=guards.values('id')).delete()
    guards.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_remove_non_repeatable_checklist_review_nt'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='gcp_review_required',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='insurance_review_required',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='legal_and_patient_review_required',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='statistical_review_required',
        ),
        migrations.RunPython(update_workflow_graphs),
        migrations.RemoveField(
            model_name='submission',
            name='external_reviewers',
        ),
    ]
