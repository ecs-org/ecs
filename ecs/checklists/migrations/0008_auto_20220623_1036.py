# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0007_remove_checklistblueprint_allow_pdf_download'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklistquestion',
            name='text',
            field=models.CharField(max_length=250),
        ),
    ]
