# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.http import QueryDict


def commit_categorizations(apps, schema_editor):
    Checklist= apps.get_model('checklists', 'Checklist')
    ChecklistBlueprint = apps.get_model('checklists', 'ChecklistBlueprint')
    DocStash = apps.get_model('docstash', 'DocStash')
    Task = apps.get_model('tasks', 'Task')

    docstashes = DocStash.objects.filter(
        group='ecs.core.views.submissions.checklist_review')

    for docstash in docstashes:
        if 'POST' in docstash.value:
            post = QueryDict(docstash.value['POST'])

            task = Task.objects.get(id=docstash.object_id)
            if task.closed_at or task.deleted_at:
                continue

            if task.task_type.workflow_node.uid == 'external_review':
                checklist = Checklist.objects.get(id=task.data_id)
            else:
                checklist = Checklist.objects.get(submission_id=task.data_id,
                    blueprint_id=task.task_type.workflow_node.data_id,
                    last_edited_by_id=docstash.owner_id)

            for q in checklist.blueprint.questions.order_by('index'):
                answer = post['checklist{}-{}-answer'.format(checklist.id, q.index)]
                comment = post['checklist{}-{}-comment'.format(checklist.id, q.index)]

                a = checklist.answers.get(question=q)
                a.answer = {
                    '1': None,
                    '2': True,
                    '3': False,
                }[answer]
                a.comment = comment
                a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0006_simplify_legal_review'),
        ('docstash', '0011_add_participatingcenternonsubject_data'),
        ('tasks', '0010_distinct_names'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(commit_categorizations),
        migrations.RunSQL('''
            delete from docstash_docstash
            where "group" = 'ecs.core.views.submissions.checklist_review';
        '''),
    ]
