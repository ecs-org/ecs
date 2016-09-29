# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0007_remove_reviews_for_b2_submissions'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            do $$
            declare
                ct_id integer;
                g_id integer;
            begin
                ct_id := (
                    select id from django_content_type
                    where app_label = 'votes' and model = 'vote'
                );

                if exists (select * from workflow_graph) then
                    insert into workflow_guard
                        (name, content_type_id, implementation)
                    values (
                        'ecs.votes.workflow.internal_vote_review_required',
                        ct_id,
                        'ecs.votes.workflow.internal_vote_review_required'
                    )
                    returning id into g_id;

                    update workflow_edge
                    set (guard_id, negated) = (g_id, false)
                    where from_node_id in (
                        select id from workflow_node
                        where uid = 'office_vote_finalization'
                    ) and to_node_id in (
                        select id from workflow_node
                        where uid = 'internal_vote_review'
                    );

                    insert into workflow_edge
                        (from_node_id, to_node_id, deadline, guard_id, negated)
                    select fn.id, tn.id, false, g_id, true
                    from workflow_node fn, workflow_node tn
                    where
                        fn.uid = 'office_vote_finalization' and
                        tn.uid = 'executive_vote_review' and
                        fn.graph_id = tn.graph_id;
                end if;
            end
            $$;
        '''),
    ]
