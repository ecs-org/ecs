# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20160929_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipatingCenterNonSubject',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('investigator_name', models.CharField(blank=True, max_length=60)),
                ('ethics_commission', models.ForeignKey(to='core.EthicsCommission')),
                ('submission_form', models.ForeignKey(to='core.SubmissionForm')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
