# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_timetable_unique_index_deferrable(apps, schema_editor):
    TimetableEntry = apps.get_model('meetings', 'TimetableEntry')

    # XXX: uses private schema editor API
    constraint_name, = schema_editor._constraint_names(TimetableEntry,
        ('meeting_id', 'timetable_index'), unique=True)

    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            alter table meetings_timetableentry drop constraint {0};
            alter table meetings_timetableentry
                add constraint {0} unique (meeting_id, timetable_index)
                    deferrable initially deferred;
        '''.format(schema_editor.quote_name(constraint_name)))


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_timetable_unique_index_deferrable),
    ]
