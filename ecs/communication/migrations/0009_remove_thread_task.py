# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0008_remove_message_reply_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='task',
        ),
    ]
