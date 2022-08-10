# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0008_auto_20220623_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklistquestion',
            name='text',
            field=models.CharField(max_length=300),
        ),
    ]
