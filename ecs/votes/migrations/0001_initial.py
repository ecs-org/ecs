# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meetings', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.CharField(max_length=2, null=True, verbose_name='vote', choices=[(b'1', '1 positive'), (b'2', '2 positive under reserve'), (b'3a', '3a recessed (not examined)'), (b'3b', '3b recessed (examined)'), (b'4', '4 negative'), (b'5', '5 withdrawn (applicant)')])),
                ('executive_review_required', models.NullBooleanField()),
                ('insurance_review_required', models.NullBooleanField()),
                ('text', models.TextField(verbose_name='comment', blank=True)),
                ('is_draft', models.BooleanField(default=False)),
                ('is_final_version', models.BooleanField(default=False)),
                ('is_expired', models.BooleanField(default=False)),
                ('signed_at', models.DateTimeField(null=True)),
                ('published_at', models.DateTimeField(null=True)),
                ('valid_until', models.DateTimeField(null=True)),
                ('changed_after_voting', models.BooleanField(default=False)),
                ('submission_form', models.ForeignKey(related_name='votes', to='core.SubmissionForm', null=True)),
                ('top', models.OneToOneField(related_name='vote', null=True, to='meetings.TimetableEntry')),
                ('upgrade_for', models.OneToOneField(related_name='previous', null=True, to='votes.Vote')),
            ],
            options={
                'get_latest_by': 'published_at',
            },
            bases=(models.Model,),
        ),
    ]
