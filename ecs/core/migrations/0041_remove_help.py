# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_participatingcenternonsubject'),
    ]

    operations = [
        migrations.RunSQL('''
            drop table help_attachment, help_page, tracking_request, tracking_view;

            delete from auth_user_groups where group_id in (
                select id from auth_group where name = 'Help Writer'
            );
            delete from auth_group where name = 'Help Writer';
        '''),
    ]
