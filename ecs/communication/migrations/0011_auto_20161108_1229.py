# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0010_auto_20161024_1236'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='origin',
        ),
        migrations.RemoveField(
            model_name='message',
            name='soft_bounced',
        ),
    ]
