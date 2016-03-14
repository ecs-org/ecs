# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_production_compat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='completionreportnotification',
            name='aborted_subjects',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='completionreportnotification',
            name='finished_subjects',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='completionreportnotification',
            name='recruited_subjects',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='progressreportnotification',
            name='aborted_subjects',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='progressreportnotification',
            name='finished_subjects',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='progressreportnotification',
            name='recruited_subjects',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
