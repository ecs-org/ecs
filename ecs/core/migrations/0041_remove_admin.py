# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_participatingcenternonsubject'),
    ]

    operations = [
        migrations.RunSQL('''
            drop table if exists django_admin_log;
        '''),
    ]
