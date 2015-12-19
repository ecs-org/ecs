# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_production_compat3'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ethicscommission',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='ethicscommission',
            name='vote_receiver',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='investigator',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='submission',
            name='befangene',
            field=models.ManyToManyField(related_name='befangen_for_submissions', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='documents',
            field=models.ManyToManyField(related_name='submission_forms', to='documents.Document'),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='invoice_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='sponsor_email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='submissionform',
            name='submitter_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
