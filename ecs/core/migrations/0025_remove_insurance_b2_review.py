# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_remove_submission_billed_at'),
        ('workflow', '0001_initial'),
        ('tasks', '0008_auto_20160621_0926'),
    ]

    operations = [
        migrations.RunSQL('''
            delete from workflow_edge
                where to_node_id in (
                    select id from workflow_node
                    where uid = 'insurance_b2_review'
                );

            delete from workflow_guard
                where implementation = 'ecs.core.workflow.needs_insurance_b2_review';
        '''),
    ]
