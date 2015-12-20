# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models.expressions import RawSQL
import uuid


def deduplicate_downloadhistory_uuid(apps, schema_editor):
    DownloadHistory = apps.get_model('documents', 'DownloadHistory')

    duplicates = (DownloadHistory.objects.order_by()
        .values('uuid')
        .annotate(count=models.Count('uuid'))
        .filter(count__gt=1))

    for duplicate in duplicates:
        hist = DownloadHistory.objects.filter(uuid=duplicate['uuid'])
        assert not hist.exclude(document__uuid=duplicate['uuid']).exists()
        for entry in hist.order_by('-downloaded_at')[1:]:
            entry.uuid = uuid.uuid4().get_hex()
            entry.save()
        assert hist.count() == 1


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_production_compat'),
    ]

    operations = [
        migrations.RunPython(deduplicate_downloadhistory_uuid),
    ]
