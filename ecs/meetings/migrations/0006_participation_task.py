# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20160621_0926'),
        ('meetings', '0005_auto_20160622_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='task',
            field=models.ForeignKey(to='tasks.Task', null=True),
        ),
    ]
