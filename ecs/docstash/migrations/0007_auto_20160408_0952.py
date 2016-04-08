# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import pickle
import zlib

from django.db import migrations, models
import django_extensions


def pickle_to_json(apps, schema_editor):
    DocStash = apps.get_model('docstash', 'DocStash')

    for docstash in DocStash.objects.all():
        value = pickle.loads(zlib.decompress(base64.b64decode(docstash.old_value)))
        docstash.value = value
        docstash.save()


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0006_auto_20160407_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='docstash',
            old_name='value',
            new_name='old_value',
        ),
        migrations.AddField(
            model_name='docstash',
            name='value',
            field=django_extensions.db.fields.json.JSONField(),
        ),
        migrations.RunPython(pickle_to_json),
        migrations.RunSQL('set constraints all immediate'),
        migrations.RemoveField(
            model_name='docstash',
            name='old_value',
        ),
    ]
