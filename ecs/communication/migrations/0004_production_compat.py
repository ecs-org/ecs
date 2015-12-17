# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0003_auto_20151217_1249'),
    ]

    operations = [
        migrations.RunSQL('''
            alter table communication_thread alter column timestamp drop default;
            alter table communication_message alter column timestamp drop default;
        ''')
    ]
