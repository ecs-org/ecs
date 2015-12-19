# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0002_auto_20151217_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='status',
            field=models.CharField(default=b'new', max_length=15, choices=[(b'new', 'New'), (b'completed', 'Completed'), (b'review_ok', 'Review OK'), (b'review_fail', 'Review Failed'), (b'dropped', 'Dropped')]),
            preserve_default=True,
        ),
    ]
