# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0007_auto_20160105_2004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='reply_to',
        ),
    ]
