# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def combine_vote_preparation(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    NodeType = apps.get_model('workflow', 'NodeType')
    Node = apps.get_model('workflow', 'Node')
    TaskType = apps.get_model('tasks', 'TaskType')

    try:
        vote_preparation_group = Group.objects.get(name='EC-Vote Preparation Group')
    except Group.DoesNotExist:
        return

    office_group = Group.objects.get(name='EC-Office')

    for user in vote_preparation_group.user_set.all():
        user.groups.add(office_group)
        user.profile.is_internal = True
        user.profile.save()
    vote_preparation_group.user_set.clear()

    Node.objects.filter(
        node_type__implementation='ecs.core.workflow.VotePreparation'
    ).update(name='Vote Preparation')

    for tt in vote_preparation_group.task_types.all():
        tt.groups.add(office_group)
        tt.name = 'Vote Preparation'
        tt.save()
    vote_preparation_group.task_types = []
    vote_preparation_group.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_initial_thesis_review_barrier'),
        ('users', '0008_remove_userprofile_is_thesis_reviewer'),
        ('auth', '0006_require_contenttypes_0002'),
        ('workflow', '0001_initial'),
        ('tasks', '0004_auto_20160308_1338'),
    ]

    operations = [
        migrations.RunPython(combine_vote_preparation),
        migrations.RunSQL('''
            update workflow_node
                set uid = 'vote_preparation'
                where uid in ('thesis_vote_preparation',
                              'expedited_vote_preparation',
                              'localec_vote_preparation');
        '''),
    ]
