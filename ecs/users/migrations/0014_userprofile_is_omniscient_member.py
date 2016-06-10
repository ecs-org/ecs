# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_omniscient_member',
            field=models.BooleanField(default=False),
        ),
    ]
