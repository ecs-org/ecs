# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_task_review_for'),
    ]

    operations = [
        migrations.RunSQL('''
            with n as (
                update workflow_node
                set name = 'Initial Amendment Review'
                where uid = 'initial_amendment_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Initial Amendment Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Initial Thesis Review'
                where uid = 'initial_thesis_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Initial Thesis Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Office Notification Review'
                where uid = 'office_report_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Office Notification Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Executive Notification Review'
                where uid = 'executive_report_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Executive Notification Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Office Vote Review (legacy)'
                where uid = 'office_vote_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Office Vote Review (legacy)'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Insurance Amendment Review'
                where uid = 'insurance_group_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Insurance Amendment Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Insurance B2 Resubmission Review'
                where uid = 'insurance_b2_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Insurance B2 Resubmission Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Office B2 Resubmission Review'
                where uid = 'b2_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Office B2 Resubmission Review'
            from n
            where workflow_node_id = n.id;

            with n as (
                update workflow_node
                set name = 'Executive B2 Resubmission Review'
                where uid = 'executive_b2_review'
                returning id
            )
            update tasks_tasktype
            set name = 'Executive B2 Resubmission Review'
            from n
            where workflow_node_id = n.id;
        '''),
    ]
