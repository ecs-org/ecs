# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_combine_vote_preparation'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsettings',
            name='display_notifications_in_protocol',
            field=models.BooleanField(default=False),
        ),
    ]
