# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def remove_empty_POST(apps, schema_migration):
    DocStash = apps.get_model('docstash', 'DocStash')
    for stash in DocStash.objects.all():
        v = stash.value
        if 'POST' in stash.value and stash.value['POST'] is None:
            del stash.value['POST']
            stash.save()


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0007_auto_20160408_0952'),
    ]

    operations = [
        migrations.RunPython(remove_empty_POST),
    ]
