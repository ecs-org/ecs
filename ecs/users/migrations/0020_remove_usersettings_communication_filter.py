# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_auto_20161125_1323'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usersettings',
            name='communication_filter',
        ),
    ]
