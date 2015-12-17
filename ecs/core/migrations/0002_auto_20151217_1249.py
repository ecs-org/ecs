# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionform',
            name='current_pending_vote',
            field=models.OneToOneField(related_name='_currently_pending_for', null=True, to='votes.Vote'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='submissionform',
            name='current_published_vote',
            field=models.OneToOneField(related_name='_currently_published_for', null=True, to='votes.Vote'),
            preserve_default=True,
        ),
    ]
