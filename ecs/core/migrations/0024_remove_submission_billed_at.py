# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160616_1236'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='billed_at',
        ),
    ]
