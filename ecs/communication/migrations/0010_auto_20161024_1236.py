# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0009_remove_thread_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='starred_by_receiver',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='thread',
            name='starred_by_sender',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL('''
            set constraints all immediate;

            update communication_thread t
            set starred_by_receiver = true
            where not closed_by_receiver and id not in (
                select thread_id from communication_message m
                where m.receiver_id = t.receiver_id and m.unread
            );

            update communication_thread t
            set starred_by_sender = true
            where not closed_by_sender and id not in (
                select thread_id from communication_message m
                where m.receiver_id = t.sender_id and m.unread
            );

            update communication_thread
            set (starred_by_sender, starred_by_receiver) = (false, false)
            where sender_id in (
                select id from auth_user where email = 'root@system.local'
            ) and id not in (
                select thread_id
                from communication_message
                where sender_id not in (
                    select id from auth_user where email = 'root@system.local'
                )
                group by thread_id
            );
        '''),
        migrations.RemoveField(
            model_name='thread',
            name='closed_by_receiver',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='closed_by_sender',
        ),
    ]
