# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boilerplate', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            alter table boilerplate_text
                alter column ctime drop default,
                alter column mtime drop default;
        ''')
    ]
