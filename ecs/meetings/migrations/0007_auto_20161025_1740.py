# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('meetings', '0006_participation_task'),
        ('tasks', '0010_distinct_names'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignedmedicalcategory',
            old_name='board_member',
            new_name='specialist',
        ),
        migrations.RunSQL('''
            do $$
            declare
                specialist_group_id integer;
            begin
                if exists (select id from auth_group where name = 'Board Member') then
                    insert into auth_group (name) values ('Specialist')
                    returning id into specialist_group_id;

                    update workflow_node
                    set (uid, name) = ('specialist_review', 'Specialist Review')
                    where uid = 'board_member_review';

                    update tasks_tasktype
                    set (name, group_id) = ('Specialist Review', specialist_group_id)
                    where workflow_node_id in (
                        select id from workflow_node
                        where uid = 'specialist_review'
                    );

                    insert into auth_user_groups (user_id, group_id)
                    select user_id, specialist_group_id from auth_user_groups
                    where group_id in (
                        select id from auth_group where name = 'Board Member'
                    );
                end if;
            end
            $$;

            update checklists_checklistblueprint
            set (name, slug) = ('Specialist Review', 'specialist_review')
            where slug = 'boardmember_review';
        '''),
    ]
