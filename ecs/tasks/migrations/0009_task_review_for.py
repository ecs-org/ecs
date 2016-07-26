# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20160621_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='review_for',
            field=models.ForeignKey(to='tasks.Task', null=True),
        ),
        migrations.RunSQL('''
            update tasks_task t
                set review_for_id = (
                    select ot.id from tasks_task ot
                    inner join tasks_tasktype ott on ott.id = ot.task_type_id
                    inner join workflow_node "on"
                        on "on".id = ott.workflow_node_id
                    where ot.closed_at is not null and
                        ot.content_type_id = t.content_type_id and
                        ot.data_id = t.data_id and "on".uid = 'categorization'
                )
                from tasks_tasktype tt, workflow_node n
                where t.task_type_id = tt.id and tt.workflow_node_id = n.id and
                    t.closed_at is null and t.deleted_at is null and
                    n.uid = 'categorization_review';

            update tasks_task t
                set review_for_id = (
                    select ot.id from tasks_task ot
                    inner join workflow_token_trail trail
                        on trail.from_token_id = t.workflow_token_id and
                            trail.to_token_id = ot.workflow_token_id
                    inner join tasks_tasktype ott on ott.id = ot.task_type_id
                    inner join workflow_node "on"
                        on "on".id = ott.workflow_node_id
                    where "on".uid not in ('start', 'b2_resubmission')
                )
                from tasks_tasktype tt, workflow_node n, workflow_nodetype nt
                where t.task_type_id = tt.id and tt.workflow_node_id = n.id and
                    n.node_type_id = nt.id and
                    t.closed_at is null and t.deleted_at is null and
                    nt.implementation in (
                        'ecs.votes.workflow.VoteReview',
                        'ecs.core.workflow.InitialB2ResubmissionReview',
                        'ecs.core.workflow.B2ResubmissionReview',
                        'ecs.notifications.workflow.EditNotificationAnswer',
                        'ecs.notifications.workflow.SimpleNotificationReview',
                        'ecs.notifications.workflow.InitialAmendmentReview'
                    );
        '''),
    ]
