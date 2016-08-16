# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_uuidfield'),
        ('core', '0031_fix_primary_investigator'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='attachment',
            field=models.ForeignKey(null=True, to='documents.Document'),
        ),
    ]
