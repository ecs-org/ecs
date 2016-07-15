# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def combine_initial_review(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    NodeType = apps.get_model('workflow', 'NodeType')
    Node = apps.get_model('workflow', 'Node')
    TaskType = apps.get_model('tasks', 'TaskType')

    try:
        thesis_review_group = Group.objects.get(name='EC-Thesis Review Group')
    except Group.DoesNotExist:
        return

    office_group = Group.objects.get(name='EC-Office')

    for user in thesis_review_group.user_set.all():
        user.groups.add(office_group)
        user.profile.is_internal = True
        user.profile.save()
    thesis_review_group.user_set.clear()

    initial_thesis_review_node_type =  NodeType.objects.get(
        implementation='ecs.core.workflow.InitialThesisReview')

    Node.objects.filter(node_type=initial_thesis_review_node_type).update(
        node_type=
            NodeType.objects.get(implementation='ecs.core.workflow.InitialReview')
    )

    initial_thesis_review_node_type.delete()

    for tt in thesis_review_group.task_types.all():
        tt.groups = [office_group]
        tt.name = 'Initial Review'
        tt.save()
    thesis_review_group.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge'),
        ('users', '0008_remove_userprofile_is_thesis_reviewer'),
        ('auth', '0006_require_contenttypes_0002'),
        ('workflow', '0001_initial'),
        ('tasks', '0004_auto_20160308_1338'),
    ]

    operations = [
        migrations.RunPython(combine_initial_review),
        migrations.RunSQL('''
            update workflow_edge
                set (guard_id, negated) = (null, false)
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'initial_review_barrier'
                );

            update workflow_edge
                set (guard_id, negated) = ((
                    select id from workflow_guard
                    where implementation = 'ecs.core.workflow.is_acknowledged_and_initial_submission'
                ), false)
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_review_barrier'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'categorization_review'
                );

            update workflow_edge
                set (guard_id, negated, to_node_id) = (null, false, (
                    select id from workflow_node
                    where uid = 'initial_review_barrier' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_edge.to_node_id
                        )
                ))
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_thesis_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'initial_thesis_review_barrier'
                );

            delete from workflow_edge
                where from_node_id in (
                        select id from workflow_node
                        where uid = 'initial_thesis_review_barrier'
                    ) or to_node_id in (
                        select id from workflow_node
                        where uid = 'initial_thesis_review_barrier'
                    );

            update workflow_token
                set source_id = (
                    select id from workflow_node
                    where uid = 'initial_review_barrier' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_token.source_id
                        )
                )
                where source_id in (
                    select id from workflow_node
                    where uid = 'initial_thesis_review_barrier'
                );

            update workflow_token
                set node_id = (
                    select id from workflow_node
                    where uid = 'initial_review_barrier' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_token.node_id
                        )
                )
                where node_id in (
                    select id from workflow_node
                    where uid = 'initial_thesis_review_barrier'
                );

            delete from workflow_node
                where uid = 'initial_thesis_review_barrier';

            delete from workflow_edge
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_thesis_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'resubmission'
                );

            update workflow_edge
                set from_node_id = (
                    select id from workflow_node
                    where uid = 'initial_review_barrier' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_edge.to_node_id
                        )
                )
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'resubmission'
                );
        '''),
    ]
