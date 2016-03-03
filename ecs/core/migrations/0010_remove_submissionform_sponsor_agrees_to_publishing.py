# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_djcelery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionform',
            name='sponsor_agrees_to_publishing',
        ),
    ]
