# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_remove_thesis_recommendation_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionform',
            name='date_of_receipt',
        ),
    ]
