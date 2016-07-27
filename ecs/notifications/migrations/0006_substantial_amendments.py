# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0005_auto_20160622_1204'),
        ('notifications', '0005_cleanup_amendment_workflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='amendmentnotification',
            name='is_substantial',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='amendmentnotification',
            name='needs_signature',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL('''
            set constraints all immediate;

            update notifications_amendmentnotification an
                set is_substantial = true
                from notifications_notification n
                where n.id = an.notification_ptr_id and
                    n.review_lane in ('insrev', 'exerev');

            do $$
            declare
                ct_id integer;
            begin
                if exists (select * from workflow_graph) then
                    ct_id := (
                        select id from django_content_type
                            where app_label = 'notifications' and
                                model = 'notification'
                    );

                    insert into workflow_guard
                        (name, content_type_id, implementation)
                    values (
                        'ecs.notifications.workflow.is_substantial',
                        ct_id,
                        'ecs.notifications.workflow.is_substantial'
                    ), (
                        'ecs.notifications.workflow.needs_signature',
                        ct_id,
                        'ecs.notifications.workflow.needs_signature'
                    ), (
                        'ecs.notifications.workflow.needs_distribution',
                        ct_id,
                        'ecs.notifications.workflow.needs_distribution'
                    );

                    insert into workflow_nodetype
                        (name, category, content_type_id, implementation)
                    values (
                        'ecs.notifications.workflow.WaitForMeeting',
                        2,      -- 'control' category
                        ct_id,
                        'ecs.notifications.workflow.WaitForMeeting'
                    );

                    insert into workflow_node (
                        name, graph_id, node_type_id, data_id, data_ct_id,
                        is_start_node, is_end_node, uid
                    )
                    select 'Amendment Split', gnt.id, nt.id, nt.id, ct.id,
                        false, false, 'amendment_split'
                    from workflow_graph g
                    inner join workflow_nodetype gnt
                        on g.nodetype_ptr_id = gnt.id and
                            gnt.content_type_id = ct_id
                    inner join django_content_type ct
                        on ct.app_label = 'workflow' and ct.model = 'nodetype'
                    inner join workflow_nodetype nt
                        on nt.implementation = 'ecs.workflow.patterns.Generic';

                    insert into workflow_node (
                        name, graph_id, node_type_id, data_id, data_ct_id,
                        is_start_node, is_end_node, uid
                    )
                    select 'Wait For Meeting', gnt.id, nt.id, nt.id, ct.id,
                        false, false, 'wait_for_meeting'
                    from workflow_graph g
                    inner join workflow_nodetype gnt
                        on g.nodetype_ptr_id = gnt.id and
                            gnt.content_type_id = ct_id
                    inner join django_content_type ct
                        on ct.app_label = 'workflow' and ct.model = 'nodetype'
                    inner join workflow_nodetype nt
                        on nt.implementation =
                            'ecs.notifications.workflow.WaitForMeeting';
                end if;
            end
            $$;

            update workflow_edge
                set to_node_id = (
                    select id from workflow_node
                    where uid = 'amendment_split' and graph_id = (
                        select graph_id from workflow_node
                        where id = workflow_edge.to_node_id
                    )
                )
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'executive_amendment_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'notification_answer_signing'
                );

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, false
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'amendment_split' and tn.uid = 'wait_for_meeting' and
                fn.graph_id = tn.graph_id and
                g.implementation = 'ecs.notifications.workflow.is_substantial' and
                tn.node_type_id in (
                    select id from workflow_nodetype where content_type_id in (
                        select id from django_content_type
                        where app_label = 'notifications' and
                            model = 'notification'
                    )
                );

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, false
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'amendment_split' and
                tn.uid = 'notification_answer_signing' and
                fn.graph_id = tn.graph_id and
                g.implementation = 'ecs.notifications.workflow.needs_signature';

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, false
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'amendment_split' and
                tn.uid = 'distribute_notification_answer' and
                fn.graph_id = tn.graph_id and
                g.implementation =
                    'ecs.notifications.workflow.needs_distribution';

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, false
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'wait_for_meeting' and
                tn.uid = 'initial_amendment_review' and
                fn.graph_id = tn.graph_id and
                g.implementation =
                    'ecs.notifications.workflow.needs_further_review' and
                fn.node_type_id in (
                    select id from workflow_nodetype where content_type_id in (
                        select id from django_content_type
                        where app_label = 'notifications' and
                            model = 'notification'
                    )
                );

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, true
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'wait_for_meeting' and
                tn.uid = 'notification_answer_signing' and
                fn.graph_id = tn.graph_id and
                g.implementation =
                    'ecs.notifications.workflow.needs_further_review' and
                fn.node_type_id in (
                    select id from workflow_nodetype where content_type_id in (
                        select id from django_content_type
                        where app_label = 'notifications' and
                            model = 'notification'
                    )
                );
        '''),
        migrations.RemoveField(
            model_name='notification',
            name='review_lane',
        ),
        migrations.AddField(
            model_name='amendmentnotification',
            name='meeting',
            field=models.ForeignKey(to='meetings.Meeting', null=True, related_name='amendments'),
        ),
    ]
