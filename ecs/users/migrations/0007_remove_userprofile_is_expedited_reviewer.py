# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_userprofile_single_login_enforced'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='is_expedited_reviewer',
        ),
    ]
