# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0006_remove_message_rawmsg_digest_hex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='smtp_delivery_state',
            field=models.CharField(default=b'new', max_length=7, db_index=True, choices=[(b'new', b'new'), (b'started', b'started'), (b'success', b'success'), (b'failure', b'failure')]),
        ),
    ]
