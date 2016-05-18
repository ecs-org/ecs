# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_convert_executive_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='befangene',
            new_name='biased_board_members',
        ),
        migrations.AlterField(
            model_name='submission',
            name='biased_board_members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, related_name='biased_for_submissions'),
        ),
    ]
