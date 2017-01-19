# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0006_simplify_legal_review'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklistblueprint',
            name='allow_pdf_download',
        ),
    ]
