# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0004_timetableentry_text'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='timetableentry',
            unique_together=set([('meeting', 'submission'), ('meeting', 'timetable_index')]),
        ),
    ]
