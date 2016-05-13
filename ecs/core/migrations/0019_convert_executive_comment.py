# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_comment'),
    ]

    operations = [
        migrations.RunSQL('''
            insert into core_comment (timestamp, text, author_id, submission_id)
                select distinct on (s.id) t.closed_at, s.executive_comment,
                    t.assigned_to_id, t.data_id
                from tasks_tasktype tt
                inner join tasks_task t
                    on t.task_type_id = tt.id and tt.name = 'Categorization Review'
                inner join core_submission s on s.id = t.data_id and
                    s.executive_comment is not null and s.executive_comment != ''
                order by s.id, t.closed_at desc;
        '''),
        migrations.RemoveField(
            model_name='submission',
            name='executive_comment',
        ),
    ]
