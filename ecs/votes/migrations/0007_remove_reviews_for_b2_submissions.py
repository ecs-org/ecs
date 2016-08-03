# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0005_fix_external_review'),
        ('core', '0030_auto_20160721_1545'),
        ('meetings', '0005_auto_20160622_1204'),
        ('tasks', '0008_auto_20160621_0926'),
        ('votes', '0006_merge'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            with t as (
                update tasks_task t
                set deleted_at = now()
                from tasks_tasktype tt, workflow_node n, django_content_type ct,
                    core_submission s, checklists_checklist cl
                where
                    t.closed_at is null and t.deleted_at is null and
                    tt.id = t.task_type_id and tt.is_dynamic and
                    n.id = tt.workflow_node_id and
                    ct.id = t.content_type_id and
                    ((
                        ct.app_label = 'core' and ct.model = 'submission' and
                        s.id = t.data_id and s.current_published_vote_id in (
                            select v.id from votes_vote v where result = '2'
                        )
                    ) or (
                        ct.app_label = 'checklists' and ct.model = 'checklist' and
                        cl.id = t.data_id and cl.submission_id = s.id and
                        s.current_published_vote_id in (
                            select v.id from votes_vote v
                            left join meetings_timetableentry e on e.id = v.top_id
                            left join meetings_meeting m on m.id = e.meeting_id
                            where result = '2' and
                                t.created_at < coalesce(m.started, v.published_at)
                        )
                    ))
                returning t.workflow_token_id
            )
            update workflow_token tok
                set consumed_at = now()
                from t
                where tok.id = t.workflow_token_id;
        '''),
    ]
