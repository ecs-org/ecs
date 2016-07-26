# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_centerclosenotification'),
        ('workflow', '0001_initial'),
        ('tasks', '0008_auto_20160621_0926'),
    ]

    operations = [
        migrations.RunSQL('''
            update workflow_edge
                set to_node_id = (
                    select id from workflow_node
                    where uid = 'executive_amendment_review' and graph_id = (
                        select graph_id from workflow_node
                        where id = workflow_edge.to_node_id
                    )
                )
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'insurance_group_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'office_insurance_review'
                );

            update workflow_edge
                set to_node_id = (
                    select id from workflow_node
                    where uid = 'executive_amendment_review' and graph_id = (
                        select graph_id from workflow_node
                        where id = workflow_edge.to_node_id
                    )
                )
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'final_notification_office_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'notification_group_review'
                );

            update workflow_edge
                set from_node_id = (
                    select id from workflow_node
                    where uid = 'executive_amendment_review' and graph_id = (
                        select graph_id from workflow_node
                        where id = workflow_edge.from_node_id
                    )
                )
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'final_executive_office_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'notification_answer_signing'
                );

            update workflow_edge
                set (guard_id, negated) = (null, false)
                where to_node_id in (
                    select id from workflow_node
                    where uid = 'executive_amendment_review'
                );

            update workflow_edge
                set (guard_id, negated) = ((
                    select id from workflow_guard
                    where implementation = 'ecs.notifications.workflow.is_rejected_and_final'
                ), true)
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_amendment_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'executive_amendment_review'
                );

            delete from workflow_edge
                where to_node_id in (
                    select id from workflow_node
                    where uid in (
                        'insurance_group_review',
                        'office_insurance_review',
                        'notification_group_review',
                        'final_notification_office_review',
                        'final_executive_office_review'
                    )
                );

            delete from workflow_edge
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'final_notification_office_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'distribute_notification_answer'
                );

            update workflow_node
                set node_type_id = (
                    select id from workflow_nodetype
                    where implementation = 'ecs.notifications.workflow.SimpleNotificationReview'
                )
                where uid in (
                    'insurance_group_review',
                    'office_insurance_review',
                    'notification_group_review',
                    'final_notification_office_review',
                    'final_executive_office_review'
                );

            update workflow_node
                set node_type_id = (
                    select id from workflow_nodetype
                    where implementation = 'ecs.notifications.workflow.EditNotificationAnswer'
                )
                where uid = 'executive_amendment_review';

            delete from workflow_nodetype
                where implementation in (
                    'ecs.notifications.workflow.InitialNotificationReview',
                    'ecs.notifications.workflow.FinalAmendmentReview',
                    'ecs.notifications.workflow.FinalAmendmentSigningReview',
                    'ecs.notifications.workflow.AmendmentReview'
                );

            update workflow_edge
                set guard_id = (
                    select id from workflow_guard
                    where implementation = 'ecs.notifications.workflow.is_rejected_and_final'
                )
                where guard_id in (
                    select id from workflow_guard
                    where implementation = 'ecs.notifications.workflow.is_rejected'
                );

            delete from workflow_guard
                where implementation in (
                    'ecs.notifications.workflow.needs_executive_group_review',
                    'ecs.notifications.workflow.needs_notification_group_review',
                    'ecs.notifications.workflow.needs_insurance_group_review',
                    'ecs.notifications.workflow.is_rejected'
                );

            insert into workflow_edge (from_node_id, to_node_id, guard_id, negated, deadline)
                select to_node_id, from_node_id, (
                    select id from workflow_guard
                    where implementation = 'ecs.notifications.workflow.needs_further_review'
                ), false, false
                from workflow_edge
                where from_node_id in (
                    select id from workflow_node
                    where uid = 'initial_amendment_review'
                ) and to_node_id in (
                    select id from workflow_node
                    where uid = 'executive_amendment_review'
                );
        '''),
    ]
