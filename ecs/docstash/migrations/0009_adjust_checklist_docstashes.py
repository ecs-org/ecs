# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.http import QueryDict


def adjust_checklist_docstashes(apps, schema_editor):
    Checklist = apps.get_model('checklists', 'Checklist')
    DocStash = apps.get_model('docstash', 'DocStash')
    Task = apps.get_model('tasks', 'Task')

    stashes = DocStash.objects.filter(
        group='ecs.core.views.submissions.checklist_review')

    for stash in stashes:
        if 'POST' in stash.value:
            post = QueryDict(stash.value['POST'], mutable=True)
            task = Task.objects.get(pk=stash.object_id)
            token = task.workflow_token
            if token.node.uid == 'external_review':
                checklist = Checklist.objects.get(id=token.workflow.data_id)
            else:
                checklist = Checklist.objects.get(
                    blueprint_id=token.node.data_id,
                    submission_id=token.workflow.data_id, user=stash.owner)

            prefix = 'checklist{}'.format(checklist.id)
            post['{}-MIN_NUM_FORMS'.format(prefix)] = '0'
            post['{}-MAX_NUM_FORMS'.format(prefix)] = '100'
            post['{}-INITIAL_FORMS'.format(prefix)] = str(checklist.answers.count())
            post['{}-TOTAL_FORMS'.format(prefix)] = str(checklist.answers.count())
            for i, answer in enumerate(checklist.answers.order_by('question__index')):
                post['{}-{}-id'.format(prefix, i)] = str(answer.id)
                post['{}-{}-answer'.format(prefix, i)] = post.pop('q{}'.format(i))[0]
                post['{}-{}-comment'.format(prefix, i)] = post.pop('c{}'.format(i))[0]

            stash.value['POST'] = post.urlencode()
            stash.save()


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0005_fix_external_review'),
        ('docstash', '0008_remove_empty_POST'),
        ('tasks', '0008_auto_20160621_0926'),
    ]

    operations = [
        migrations.RunPython(adjust_checklist_docstashes),
    ]
