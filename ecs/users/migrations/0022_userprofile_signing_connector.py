# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_rename_executive'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='signing_connector',
            field=models.CharField(max_length=9, choices=[('bku', 'localbku'), ('onlinebku', 'onlinebku'), ('mobilebku', 'mobilebku')], default='onlinebku'),
        ),
    ]
