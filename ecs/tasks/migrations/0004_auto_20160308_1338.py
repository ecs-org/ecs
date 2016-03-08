# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_merge_medical_categories'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='expedited_review_categories',
            new_name='medical_categories',
        ),
    ]
