# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0001_initial'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            update workflow_edge
                set (guard_id, negated) = (null, false)
                where guard_id in (
                    select id from workflow_guard
                    where implementation = 'ecs.votes.workflow.is_executive_vote_review_required'
                ) and negated;

            delete from workflow_edge
                where guard_id in (
                    select id from workflow_guard
                    where implementation = 'ecs.votes.workflow.is_executive_vote_review_required'
                ) and not negated;

            delete from workflow_guard
                where implementation = 'ecs.votes.workflow.is_executive_vote_review_required';
        '''),
    ]
