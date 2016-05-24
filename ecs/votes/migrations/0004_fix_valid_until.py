# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0003_vote_published_by'),
    ]

    operations = [
        migrations.RunSQL('''
            update votes_vote
                set (valid_until, is_expired) = (null, false)
                where result != '1';

            update core_submission
                set is_expired = id in (
                    select sf.submission_id from votes_vote v
                        inner join core_submissionform sf on sf.id = v.submission_form_id
                        where v.is_expired
                );
        '''),
    ]
