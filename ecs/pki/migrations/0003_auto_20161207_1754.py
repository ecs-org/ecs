# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0002_production_compat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='cn',
            field=models.CharField(unique=True, max_length=64),
        ),
    ]
