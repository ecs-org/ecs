# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_production_compat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginhistory',
            name='ip',
            field=models.GenericIPAddressField(protocol=b'IPv4'),
            preserve_default=True,
        ),
    ]
