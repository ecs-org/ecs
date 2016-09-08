# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_substantial_amendments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='date_of_receipt',
        ),
    ]
