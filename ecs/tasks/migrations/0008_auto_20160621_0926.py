# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_tasktype_is_dynamic'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='reminder_message_sent_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='reminder_message_timeout',
            field=models.DurationField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='send_message_on_close',
            field=models.BooleanField(default=False),
        ),
    ]
