# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0043_auto_20161202_1132'),
        ('tasks', '0010_distinct_names'),
        ('votes', '0008_optional_internal_vote_review'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            with workflow_token_ids as (
                with task_ids as (
                    select t.id from tasks_task t
                    inner join tasks_tasktype tt on tt.id = t.task_type_id and tt.is_dynamic
                    inner join django_content_type ct on ct.id = t.content_type_id
                    left join checklists_checklist c on c.id = t.data_id and
                        ct.app_label = 'checklists' and ct.model = 'checklist'
                    inner join core_submission s on
                        s.id = c.submission_id or
                        (s.id = t.data_id and ct.app_label = 'core' and ct.model = 'submission')
                    left join votes_vote v on v.id = s.current_published_vote_id
                    where t.closed_at is null and t.deleted_at is null and
                        (s.is_expired or s.is_finished or v.result in ('4', '5'))
                )
                update tasks_task
                set deleted_at = now()
                from task_ids
                where tasks_task.id = task_ids.id
                returning workflow_token_id as id
            )
            update workflow_token
            set consumed_at = now()
            from workflow_token_ids
            where workflow_token.id = workflow_token_ids.id;
        '''),
    ]
