# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('tasks', '0008_auto_20160621_0926'),
        ('users', '0014_userprofile_is_omniscient_member'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='task_uids',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=100), size=None),
        ),
        migrations.RunSQL('''
            update users_userprofile set task_uids = ut.task_uids
                from (
                    select
                        ug.user_id,
                        array_agg(distinct n.uid order by n.uid) as task_uids
                    from auth_user_groups ug
                    inner join auth_group g on g.id = ug.group_id and g.name in (
                        'EC-Signing',
                        'EC-Office',
                        'EC-Internal Reviewer',
                        'EC-B2 Reviewer',
                        'EC-Notification Reviewer',
                        'EC-Paper Submission Reviewer',
                        'EC-Safety Report Reviewer',
                        'EC-Thesis Executive Group',
                        'EC-Executive Board Member',
                        'External Review Reviewer',
                        'Local-EC Reviewer'
                    )
                    inner join tasks_tasktype tt on tt.group_id = g.id
                    inner join workflow_node n on n.id = tt.workflow_node_id
                    group by ug.user_id
                ) ut
                where users_userprofile.user_id = ut.user_id;


            update tasks_tasktype
                set group_id = (
                    select id from auth_group where name = 'EC-Office'
                )
                where group_id in (
                    select id from auth_group
                    where name in (
                        'EC-Internal Reviewer',
                        'EC-B2 Reviewer',
                        'EC-Notification Reviewer',
                        'EC-Paper Submission Reviewer',
                        'EC-Safety Report Reviewer',
                        'EC-Thesis Executive Group'
                    )
                );

            update tasks_tasktype
                set group_id = (
                    select id from auth_group where name = 'EC-Executive Board Member'
                )
                where group_id in (
                    select id from auth_group
                    where name in (
                        'External Review Reviewer',
                        'Local-EC Reviewer'
                    )
                );

            insert into auth_user_groups (user_id, group_id)
                select ug.user_id, office_group.id from auth_user_groups ug
                inner join auth_group office_group on office_group.name = 'EC-Office'
                inner join auth_group g on g.id = ug.group_id and g.name in (
                    'EC-Internal Reviewer',
                    'EC-B2 Reviewer',
                    'EC-Notification Reviewer',
                    'EC-Paper Submission Reviewer',
                    'EC-Safety Report Reviewer',
                    'EC-Thesis Executive Group'
                )
                except select user_id, group_id from auth_user_groups;

            insert into auth_user_groups (user_id, group_id)
                select ug.user_id, office_group.id from auth_user_groups ug
                inner join auth_group office_group on office_group.name = 'EC-Executive Board Member'
                inner join auth_group g on g.id = ug.group_id and g.name in (
                    'External Review Reviewer',
                    'Local-EC Reviewer'
                )
                except select user_id, group_id from auth_user_groups;

            delete from auth_user_groups
                where group_id in (
                    select id from auth_group
                    where name in (
                        'EC-Internal Reviewer',
                        'EC-B2 Reviewer',
                        'EC-Notification Reviewer',
                        'EC-Paper Submission Reviewer',
                        'EC-Safety Report Reviewer',
                        'EC-Thesis Executive Group',
                        'External Review Reviewer',
                        'Local-EC Reviewer'
                    )
                );

            delete from auth_group
                where name in (
                    'EC-Internal Reviewer',
                    'EC-B2 Reviewer',
                    'EC-Notification Reviewer',
                    'EC-Paper Submission Reviewer',
                    'EC-Safety Report Reviewer',
                    'EC-Thesis Executive Group',
                    'External Review Reviewer',
                    'Local-EC Reviewer'
                );

            update auth_group set name = 'Board Member'
                where name = 'EC-Board Member';

            update auth_group set name = 'Insurance Reviewer'
                where name = 'EC-Insurance Reviewer';

            update auth_group set name = 'Statistic Reviewer'
                where name = 'EC-Statistic Reviewer';
        '''),
    ]
