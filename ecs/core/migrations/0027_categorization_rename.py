# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_remove_start_node'),
        ('docstash', '0008_remove_empty_POST'),
        ('tasks', '0008_auto_20160621_0926'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            update workflow_nodetype
                set (implementation, name) = (
                    'ecs.core.workflow.Categorization',
                    'ecs.core.workflow.Categorization'
                )
                where implementation = 'ecs.core.workflow.CategorizationReview';

            update workflow_node
                set (name, uid) = ('Categorization', 'categorization')
                where uid = 'categorization_review';

            update tasks_tasktype
                set name = 'Categorization'
                where name = 'Categorization Review';

            update docstash_docstash
                set "group" = 'ecs.core.views.submissions.categorization'
                where "group" = 'ecs.core.views.submissions.categorization_review';
        '''),
    ]
