# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0004_fix_valid_until'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            create temporary view start_nodes as
                select n.* from workflow_node n
                inner join workflow_nodetype nt on n.graph_id = nt.id
                where nt.content_type_id = (
                    select id from django_content_type
                    where app_label = 'votes' and model = 'vote'
                ) and uid = 'start';

            delete from workflow_token_trail
                where from_token_id in (
                    select id from workflow_token
                    where node_id in (select id from start_nodes)
                ) or to_token_id in (
                    select id from workflow_token
                    where node_id in (select id from start_nodes)
                );

            delete from workflow_token
                where node_id in (select id from start_nodes);

            update workflow_token
                set source_id = null
                where source_id in (select id from start_nodes);

            delete from workflow_edge
                where from_node_id in (select id from start_nodes);

            delete from workflow_node
                where id in (select id from start_nodes);

            drop view start_nodes;

            update workflow_node
                set is_start_node = true
                where graph_id in (
                    select id from workflow_nodetype
                    where content_type_id = (
                        select id from django_content_type
                        where app_label = 'votes' and model = 'vote'
                    )
                ) and uid = 'office_vote_finalization';

            delete from workflow_nodetype
                where implementation in ('ecs.votes.workflow.VoteB2Review',
                                         'ecs.votes.workflow.VoteFinalization',
                                         'ecs.votes.workflow.B2Resubmission');
        '''),
    ]
