# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            alter table docstash_docstashdata alter column modtime drop default;
        ''')
    ]
