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

            delete from workflow_edge
                where from_node_id in (
                        select id from workflow_node
                        where uid in ('initial_review_barrier',
                                      'initial_thesis_review_barrier')
                    ) and to_node_id in (
                        select id from workflow_node
                        where uid in ('categorization_review', 'thesis_recommendation')
                    );

            delete from workflow_edge
                where from_node_id in (
                        select id from workflow_node
                        where uid = 'wait_for_meeting'
                    ) or to_node_id in (
                        select id from workflow_node
                        where uid in ('wait_for_meeting', 'initial_thesis_review')
                    );

            update workflow_edge
                set to_node_id = (
                    select id from workflow_node
                    where uid = 'categorization_review' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_edge.to_node_id
                        )
                )
                where from_node_id in (
                        select id from workflow_node
                        where uid in ('initial_review', 'initial_thesis_review')
                    ) and to_node_id in (
                        select id from workflow_node
                        where uid in ('initial_review_barrier',
                                      'initial_thesis_review_barrier')
                    );

            update workflow_edge
                set from_node_id = (
                    select id from workflow_node
                    where uid = 'initial_review' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_edge.from_node_id
                        )
                )
                where from_node_id in (
                        select id from workflow_node
                        where uid = 'initial_review_barrier'
                    ) and to_node_id in (
                        select id from workflow_node
                        where uid = 'paper_submission_review'
                    );

            update workflow_edge
                set from_node_id = (
                    select id from workflow_node
                    where uid = 'initial_thesis_review' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_edge.from_node_id
                        )
                ), guard_id = (
                    select id from workflow_guard
                    where implementation = 'ecs.core.workflow.is_acknowledged_and_initial_submission'
                )
                where from_node_id in (
                        select id from workflow_node
                        where uid = 'initial_thesis_review_barrier'
                    ) and to_node_id in (
                        select id from workflow_node
                        where uid = 'paper_submission_review'
                    );

            update workflow_edge
                set (guard_id, negated) = (null, false)
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'start'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'initial_review'
                );

            insert into workflow_token_trail (from_token_id, to_token_id)
                select t1.from_token_id, t2.to_token_id from workflow_token_trail t1
                    inner join workflow_token_trail t2
                        on t1.to_token_id in (
                            select id from workflow_token where node_id in (
                                    select id from workflow_node
                                    where uid in ('initial_review_barrier',
                                                  'initial_thesis_review_barrier')
                                )
                        ) and t1.to_token_id = t2.from_token_id;

            delete from workflow_token_trail
                where from_token_id in (
                    select id from workflow_token where node_id in (
                        select id from workflow_node
                        where uid in ('initial_review_barrier',
                                      'initial_thesis_review_barrier',
                                      'wait_for_meeting')
                    )
                ) or to_token_id in (
                    select id from workflow_token where node_id in (
                        select id from workflow_node
                        where uid in ('initial_review_barrier',
                                      'initial_thesis_review_barrier',
                                      'wait_for_meeting')
                    )
                );

            update workflow_token
                set source_id = null
                where source_id in (
                    select id from workflow_node
                    where uid = 'wait_for_meeting'
                );

            update workflow_token
                set source_id = (
                    select id from workflow_node
                    where uid = 'initial_thesis_review' and
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
                set source_id = (
                    select id from workflow_node
                    where uid = 'initial_review' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_token.source_id
                        )
                )
                where source_id in (
                    select id from workflow_node
                    where uid = 'initial_review_barrier'
                );

            delete from workflow_token
                where node_id in (
                    select id from workflow_node
                    where uid in ('initial_review_barrier',
                                  'initial_thesis_review_barrier',
                                  'wait_for_meeting')
                );

            delete from workflow_node
                where uid in ('initial_review_barrier',
                              'initial_thesis_review_barrier',
                              'wait_for_meeting');

            delete from workflow_nodetype
                where implementation = 'ecs.core.workflow.WaitForMeeting';
        '''),
    ]
