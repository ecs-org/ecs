# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0011_auto_20161108_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='unread',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='starred_by_receiver',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='thread',
            name='starred_by_sender',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
