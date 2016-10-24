# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_remove_userprofile_is_insurance_reviewer'),
    ]

    operations = [
        migrations.RunSQL('''
            update users_usersettings
            set communication_filter = '{}'::json;
        '''),
    ]
