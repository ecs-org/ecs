# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0007_remove_notification_date_of_receipt'),
        ('tasks', '0010_distinct_names'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='safetynotification',
            name='is_acknowledged',
        ),
        migrations.RemoveField(
            model_name='safetynotification',
            name='reviewer',
        ),
        migrations.RunSQL('''
            update workflow_node
            set node_type_id = (
                select id from workflow_nodetype
                where implementation = 'ecs.notifications.workflow.SimpleNotificationReview'
            ) where uid = 'safety_review';

            delete from workflow_nodetype
            where implementation = 'ecs.notifications.workflow.SafetyNotificationReview';

            update workflow_edge
            set (guard_id, negated) = ((
                select id from workflow_guard
                where name = 'ecs.notifications.workflow.is_rejected_and_final'
            ), false)
            where from_node_id in (
                select id from workflow_node where uid = 'safety_review'
            ) and to_node_id in (
                select id from workflow_node
                where uid = 'distribute_notification_answer'
            );

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, true
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'safety_review' and
                tn.uid = 'executive_report_review' and
                fn.graph_id = tn.graph_id and
                g.implementation = 'ecs.notifications.workflow.is_rejected_and_final';

            update workflow_edge
            set (guard_id, negated) = ((
                select id from workflow_guard
                where name = 'ecs.notifications.workflow.is_rejected_and_final'
            ), true)
            where from_node_id in (
                select id from workflow_node where uid = 'office_report_review'
            ) and to_node_id in (
                select id from workflow_node
                where uid = 'executive_report_review'
            );

            insert into workflow_edge
                (from_node_id, to_node_id, deadline, guard_id, negated)
            select fn.id, tn.id, false, g.id, false
            from workflow_node fn, workflow_node tn, workflow_guard g
            where fn.uid = 'office_report_review' and
                tn.uid = 'distribute_notification_answer' and
                fn.graph_id = tn.graph_id and
                g.implementation = 'ecs.notifications.workflow.is_rejected_and_final';

            update workflow_edge
            set to_node_id = (
                select nwn.id from
                workflow_node nwn, workflow_node own
                where own.id = workflow_edge.to_node_id and
                    nwn.uid = 'start' and own.graph_id = nwn.graph_id
            ) where from_node_id in (
                select id from workflow_node where uid = 'executive_report_review'
            ) and to_node_id in (
                select id from workflow_node
                where uid = 'office_report_review'
            );

        '''),
    ]
