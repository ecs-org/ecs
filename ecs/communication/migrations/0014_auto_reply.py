# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0013_search_tsvector'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='rawmsg_msgid',
            new_name='outgoing_msgid',
        ),
        migrations.AddField(
            model_name='message',
            name='creator',
            field=models.CharField(choices=[('human', 'human'), ('auto-self', 'auto-self'), ('auto-custom', 'auto-custom'), ('auto-generated', 'auto-generated'), ('auto-replied', 'auto-replied'), ('auto-notified', 'auto-notified')], max_length=14, default='human'),
        ),
        migrations.AddField(
            model_name='message',
            name='in_reply_to',
            field=models.ForeignKey(related_name='is_replied_in', null=True, default=None, to='communication.Message'),
        ),
        migrations.AddField(
            model_name='message',
            name='incoming_msgid',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
