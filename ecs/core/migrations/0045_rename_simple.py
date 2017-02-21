# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0007_remove_checklistblueprint_allow_pdf_download'),
        ('core', '0044_auto_20170203_1351'),
        ('users', '0021_rename_executive'),
        ('workflow', '0002_auto_20170119_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='workflow_lane',
            field=models.SmallIntegerField(choices=[(3, 'board'), (2, 'expedited'), (1, 'simple'), (4, 'Local EC')], null=True, db_index=True),
        ),
        migrations.RunSQL('''
            update workflow_guard
            set (name, implementation) = (
                'ecs.core.workflow.is_simple',
                'ecs.core.workflow.is_simple'
            )
            where implementation = 'ecs.core.workflow.is_retrospective_thesis';

            update workflow_guard
            set (name, implementation) = (
                'ecs.core.workflow.has_simple_recommendation',
                'ecs.core.workflow.has_simple_recommendation'
            )
            where implementation = 'ecs.core.workflow.has_thesis_recommendation';

            update workflow_guard
            set (name, implementation) = (
                'ecs.core.workflow.needs_simple_vote_preparation',
                'ecs.core.workflow.needs_simple_vote_preparation'
            )
            where implementation = 'ecs.core.workflow.needs_thesis_vote_preparation';

            delete from workflow_guard where implementation =
                'ecs.core.workflow.is_expedited_or_retrospective_thesis';

            update workflow_node
            set (uid, name) = ('simple_recommendation', 'Simple Recommendation')
            where uid = 'thesis_recommendation';

            update tasks_tasktype
            set name = 'Simple Recommendation'
            where workflow_node_id in (
                select id from workflow_node where uid = 'simple_recommendation'
            );

            update checklists_checklistblueprint
            set (name, slug) = ('Simple Review', 'simple_review')
            where slug = 'thesis_review';

            update users_userprofile
            set task_uids = array_replace(task_uids,
                'thesis_recommendation', 'simple_recommendation');
        '''),
    ]
