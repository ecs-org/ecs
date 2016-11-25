# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('users', '0018_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='has_explicit_workflow',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_have_open_tasks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='can_have_tasks',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL('''
            update users_userprofile up
            set can_have_tasks = true
            from auth_user_groups ug, auth_group g
            where up.user_id = ug.user_id and ug.group_id = g.id and g.name in (
                'Board Member',
                'EC-Executive Board Member',
                'EC-Office',
                'EC-Signing',
                'GCP Reviewer',
                'Insurance Reviewer',
                'Statistic Reviewer',
                'External Reviewer',
                'Specialist'
            );

            update users_userprofile up
            set can_have_open_tasks = true
            from auth_user_groups ug, auth_group g
            where up.user_id = ug.user_id and ug.group_id = g.id and g.name in (
                'Board Member',
                'EC-Executive Board Member',
                'EC-Office',
                'EC-Signing',
                'GCP Reviewer',
                'Insurance Reviewer',
                'Statistic Reviewer'
            );
        '''),
    ]
