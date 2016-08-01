# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsettings',
            name='display_biased_in_amendment_answer_pdf',
            field=models.BooleanField(default=True),
        ),
    ]
