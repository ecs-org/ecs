# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_auto_20161202_1132'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='investigator',
            options={'ordering': ['-main', 'id']},
        ),
    ]
