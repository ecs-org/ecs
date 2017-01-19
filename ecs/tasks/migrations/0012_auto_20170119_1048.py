# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_delete_obsolete_tasks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='closed_at',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='deleted_at',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
