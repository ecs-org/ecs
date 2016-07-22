# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_comment_attachment'),
    ]

    operations = [
        migrations.RunSQL('''
            update workflow_node
                set node_type_id = (
                    select id from workflow_nodetype
                    where implementation = 'ecs.core.workflow.ChecklistReview'
                )
                where node_type_id = (
                    select id from workflow_nodetype
                    where implementation = 'ecs.core.workflow.RecommendationReview'
                );

            delete from workflow_nodetype
                where implementation = 'ecs.core.workflow.RecommendationReview';

            do $$
            declare
                ct_id integer;
            begin
                ct_id := (
                    select id from django_content_type
                    where app_label = 'core' and model = 'submission'
                );

                if exists (select * from workflow_graph) then
                    insert into workflow_guard
                        (name, content_type_id, implementation)
                    values (
                        'ecs.core.workflow.needs_thesis_vote_preparation',
                        ct_id,
                        'ecs.core.workflow.needs_thesis_vote_preparation'
                    );
                end if;
            end
            $$;

            update workflow_edge
                set (to_node_id, guard_id, negated) = ((
                    select n.id from workflow_node n
                    inner join workflow_edge e on e.to_node_id = n.id
                    where n.uid = 'vote_preparation' and
                        graph_id = (
                            select graph_id from workflow_node
                            where id = workflow_edge.to_node_id
                        ) and e.from_node_id in (
                            select id from workflow_node
                            where uid = 'thesis_recommendation_review'
                        )
                ), (
                    select id from workflow_guard
                    where implementation =
                        'ecs.core.workflow.needs_thesis_vote_preparation'
                ), false)
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'thesis_recommendation'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'thesis_recommendation_review'
                );
        '''),
    ]
