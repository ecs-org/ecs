# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0004_fix_valid_until'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='insurance_review_required',
        ),
    ]
