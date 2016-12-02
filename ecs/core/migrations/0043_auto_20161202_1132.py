# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigator',
            name='ethics_commission',
            field=models.ForeignKey(to='core.EthicsCommission', related_name='investigators'),
        ),
    ]
