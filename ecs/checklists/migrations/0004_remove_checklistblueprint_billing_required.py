# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0003_auto_20151219_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklistblueprint',
            name='billing_required',
        ),
    ]
