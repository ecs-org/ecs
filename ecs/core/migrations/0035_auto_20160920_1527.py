# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_remove_submissionform_date_of_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsettings',
            name='logo',
            field=models.BinaryField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='logo_mimetype',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='print_logo',
            field=models.BinaryField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='print_logo_mimetype',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
