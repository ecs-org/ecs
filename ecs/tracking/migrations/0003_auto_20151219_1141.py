# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_production_compat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='ip',
            field=models.GenericIPAddressField(protocol=b'IPv4', db_index=True),
            preserve_default=True,
        ),
    ]
