# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_users(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            select count(*) from information_schema.columns
            where table_name='users_usersettings' and column_name = 'pdfviewer_settings'
        ''')
        if cursor.fetchone()[0]:
            cursor.execute("select id from auth_group where name = 'sentryusers'")
            sentry_group_id = cursor.fetchone()[0]

            cursor.execute('''
                alter table users_usersettings drop column pdfviewer_settings;
                alter table users_userprofile
                    add column is_developer boolean,
                    alter column last_password_change drop default;
                update users_userprofile
                    set is_developer = (user_id in (
                        select user_id from auth_user_groups
                        where group_id = %(sentry_group_id)s));
                alter table users_userprofile
                    alter column is_developer set not null;

                delete from auth_user_groups where group_id = %(sentry_group_id)s;
                delete from auth_group_permissions where permission_id in (
                    select auth_permission.id from auth_permission
                    join django_content_type
                        on django_content_type.id = auth_permission.content_type_id and
                            django_content_type.app_label = 'sentry' );
                delete from auth_permission where content_type_id in (
                    select id from django_content_type where app_label = 'sentry');
                delete from django_content_type where app_label = 'sentry';
                delete from auth_group where id = %(sentry_group_id)s;
            ''', {'sentry_group_id': sentry_group_id})



class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_users),
    ]
