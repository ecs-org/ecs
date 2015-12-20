# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedMedicalCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('board_member', models.ForeignKey(related_name='assigned_medical_categories', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('category', models.ForeignKey(to='core.MedicalCategory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Constraint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('weight', models.FloatField(default=0.5, choices=[(1.0, 'impossible'), (0.5, 'unfavorable')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('title', models.CharField(max_length=200)),
                ('optimization_task_id', models.TextField(null=True)),
                ('started', models.DateTimeField(null=True)),
                ('ended', models.DateTimeField(null=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('deadline', models.DateTimeField(null=True)),
                ('deadline_diplomathesis', models.DateTimeField(null=True)),
                ('agenda_sent_at', models.DateTimeField(null=True)),
                ('protocol_sent_at', models.DateTimeField(null=True)),
                ('expedited_reviewer_invitation_sent_for', models.DateTimeField(null=True)),
                ('expedited_reviewer_invitation_sent_at', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ignored_for_optimization', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimetableEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('timetable_index', models.IntegerField(null=True)),
                ('duration_in_seconds', models.PositiveIntegerField()),
                ('is_break', models.BooleanField(default=False)),
                ('optimal_start', models.TimeField(null=True)),
                ('is_open', models.BooleanField(default=True)),
                ('meeting', models.ForeignKey(related_name='timetable_entries', to='meetings.Meeting')),
                ('submission', models.ForeignKey(related_name='timetable_entries', to='core.Submission', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='timetableentry',
            unique_together=set([('meeting', 'timetable_index')]),
        ),
        migrations.AddField(
            model_name='participation',
            name='entry',
            field=models.ForeignKey(related_name='participations', to='meetings.TimetableEntry'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participation',
            name='medical_category',
            field=models.ForeignKey(related_name='meeting_participations', blank=True, to='core.MedicalCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participation',
            name='user',
            field=models.ForeignKey(related_name='meeting_participations', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meeting',
            name='submissions',
            field=models.ManyToManyField(related_name='meetings', through='meetings.TimetableEntry', to='core.Submission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constraint',
            name='meeting',
            field=models.ForeignKey(related_name='constraints', to='meetings.Meeting'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='constraint',
            name='user',
            field=models.ForeignKey(related_name='meeting_constraints', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignedmedicalcategory',
            name='meeting',
            field=models.ForeignKey(related_name='medical_categories', to='meetings.Meeting'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='assignedmedicalcategory',
            unique_together=set([('category', 'meeting')]),
        ),
    ]
