# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_remove_submissionform_date_of_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsettings',
            name='require_internal_vote_review',
            field=models.BooleanField(default=False),
        ),
        migrations.RunSQL('''
            update core_advancedsettings
                set require_internal_vote_review = true;
        '''),
    ]
