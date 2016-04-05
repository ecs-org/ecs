# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_userprofile_is_expedited_reviewer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='is_thesis_reviewer',
        ),
    ]
