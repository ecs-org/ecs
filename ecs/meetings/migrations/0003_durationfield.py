# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0002_defer_timetable_index_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetableentry',
            name='duration',
            field=models.DurationField(null=True),
        ),
        migrations.RunSQL('''
            update meetings_timetableentry
                set duration = '1 second'::interval * duration_in_seconds;
        '''),
        migrations.AlterField(
            model_name='timetableentry',
            name='duration',
            field=models.DurationField(),
        ),
        migrations.RemoveField(
            model_name='timetableentry',
            name='duration_in_seconds',
        ),
    ]
