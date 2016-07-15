# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_categorization_rename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='remission',
            field=models.BooleanField(default=False),
        ),
    ]
