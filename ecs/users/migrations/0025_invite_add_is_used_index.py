# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_invite_add_created_rename_accepted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='is_used',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
