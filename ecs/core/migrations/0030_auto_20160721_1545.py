# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0006_merge'),
        ('core', '0029_advancedsettings_display_biased_in_amendment_answer_pdf'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionform',
            name='current_pending_vote',
        ),
        migrations.RemoveField(
            model_name='submissionform',
            name='current_published_vote',
        ),
        migrations.AddField(
            model_name='submission',
            name='current_pending_vote',
            field=models.OneToOneField(null=True, to='votes.Vote', related_name='_currently_pending_for'),
        ),
        migrations.AddField(
            model_name='submission',
            name='current_published_vote',
            field=models.OneToOneField(null=True, to='votes.Vote', related_name='_currently_published_for'),
        ),
        migrations.RunSQL('''
            set constraints all immediate;

            update core_submission
                set (current_pending_vote_id, current_published_vote_id) = (
                    (
                        select v.id from core_submissionform sf
                        inner join votes_vote v on v.submission_form_id = sf.id
                            and v.published_at is null
                        where sf.submission_id = core_submission.id
                        order by v.id desc
                        limit 1
                    ),
                    (
                        select v.id from core_submissionform sf
                        inner join votes_vote v on v.submission_form_id = sf.id
                            and v.published_at is not null
                        where sf.submission_id = core_submission.id
                        order by v.published_at desc
                        limit 1
                    )
                );

            -- Handle old draft votes hanging around, caused by a bug producing
            -- duplicate draft votes.
            update core_submission
                set current_pending_vote_id = null
                where current_pending_vote_id < current_published_vote_id;

            delete from workflow_guard
                where implementation = 'ecs.core.workflow.is_b2';
        ''', ''),
    ]
