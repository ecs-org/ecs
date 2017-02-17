# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('core', '0044_auto_20170203_1351'),
        ('users', '0020_remove_usersettings_communication_filter'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_executive_board_member',
            new_name='is_executive',
        ),
        migrations.RunSQL('''
            update auth_group
            set name = 'EC-Executive'
            where name = 'EC-Executive Board Member';
        ''', '''
            update auth_group
            set name = 'EC-Executive Board Member'
            where name = 'EC-Executive';
        '''),
    ]
