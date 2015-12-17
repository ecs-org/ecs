# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='submission',
            field=models.ForeignKey(to='core.Submission', null=True),
            preserve_default=True,
        ),
    ]
