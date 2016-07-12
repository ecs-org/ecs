# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0004_fix_valid_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='submission_form',
            field=models.ForeignKey(related_name='votes', to='core.SubmissionForm'),
        ),
    ]
