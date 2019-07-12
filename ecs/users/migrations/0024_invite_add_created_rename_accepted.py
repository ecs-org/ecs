# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_remove_userprofile_social_security_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitation',
            old_name='is_accepted',
            new_name='is_used',
        ),
        migrations.AddField(
            model_name='invitation',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
