# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_remove_submission_billed_at'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            delete from workflow_edge
                where from_node_id in (
                        select id from workflow_node
                        where uid = 'wait_for_meeting'
                    ) or to_node_id in (
                        select id from workflow_node
                        where uid = 'wait_for_meeting'
                    );

            delete from workflow_token_trail
                where from_token_id in (
                    select id from workflow_token where node_id in (
                        select id from workflow_node
                        where uid = 'wait_for_meeting'
                    )
                ) or to_token_id in (
                    select id from workflow_token where node_id in (
                        select id from workflow_node
                        where uid = 'wait_for_meeting'
                    )
                );

            update workflow_token
                set source_id = null
                where source_id in (
                    select id from workflow_node
                    where uid = 'wait_for_meeting'
                );

            delete from workflow_token
                where node_id in (
                    select id from workflow_node
                    where uid = 'wait_for_meeting'
                );

            delete from workflow_node
                where uid = 'wait_for_meeting';

            delete from workflow_nodetype
                where implementation = 'ecs.core.workflow.WaitForMeeting';

            update workflow_edge
                set guard_id = (
                    select id from workflow_guard
                    where implementation = 'ecs.core.workflow.is_acknowledged_and_initial_submission'
                )
                where guard_id = (
                    select id from workflow_guard
                    where implementation = 'ecs.core.workflow.needs_paper_submission_review'
                );

            update workflow_edge
                set (guard_id, negated) = ((
                    select id from workflow_guard
                    where implementation = 'ecs.core.workflow.needs_expedited_recategorization'
                ), false)
                where guard_id = (
                    select id from workflow_guard
                    where implementation = 'ecs.core.workflow.has_expedited_recommendation'
                ) and negated = true;

            delete from workflow_guard
                where implementation in ('ecs.core.workflow.is_initial_submission',
                                         'ecs.core.workflow.needs_paper_submission_review',
                                         'ecs.core.workflow.has_expedited_recommendation');
        '''),
    ]
