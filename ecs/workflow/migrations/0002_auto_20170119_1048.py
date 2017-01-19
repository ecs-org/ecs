# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='uid',
            field=models.CharField(max_length=100, db_index=True, null=True),
        ),
    ]
