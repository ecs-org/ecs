# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_auto_20151217_1249'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comments', models.TextField()),
                ('date_of_receipt', models.DateField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('review_lane', models.CharField(db_index=True, max_length=6, null=True, choices=[(b'exerev', b'Executive Review'), (b'notrev', b'Notification Group Review'), (b'insrev', b'Insurance Group Review')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompletionReportNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.Notification')),
                ('study_started', models.BooleanField(default=True)),
                ('reason_for_not_started', models.TextField(null=True, blank=True)),
                ('recruited_subjects', models.IntegerField(null=True)),
                ('finished_subjects', models.IntegerField(null=True)),
                ('aborted_subjects', models.IntegerField(null=True)),
                ('SAE_count', models.PositiveIntegerField(default=0)),
                ('SUSAR_count', models.PositiveIntegerField(default=0)),
                ('study_aborted', models.BooleanField(default=False)),
                ('completion_date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
            bases=('notifications.notification',),
        ),
        migrations.CreateModel(
            name='AmendmentNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.Notification')),
                ('new_submission_form', models.ForeignKey(related_name='new_for_notification', to='core.SubmissionForm')),
                ('old_submission_form', models.ForeignKey(related_name='old_for_notification', to='core.SubmissionForm')),
            ],
            options={
                'abstract': False,
            },
            bases=('notifications.notification', models.Model),
        ),
        migrations.CreateModel(
            name='NotificationAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('is_valid', models.BooleanField(default=True)),
                ('is_final_version', models.BooleanField(default=False, verbose_name='Proofread')),
                ('is_rejected', models.BooleanField(default=False, verbose_name='rate negative')),
                ('signed_at', models.DateTimeField(null=True)),
                ('published_at', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80)),
                ('form', models.CharField(default=b'ecs.notifications.forms.NotificationForm', max_length=80)),
                ('default_response', models.TextField(blank=True)),
                ('position', models.IntegerField(default=0)),
                ('includes_diff', models.BooleanField(default=False)),
                ('grants_vote_extension', models.BooleanField(default=False)),
                ('finishes_study', models.BooleanField(default=False)),
                ('is_rejectable', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgressReportNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.Notification')),
                ('study_started', models.BooleanField(default=True)),
                ('reason_for_not_started', models.TextField(null=True, blank=True)),
                ('recruited_subjects', models.IntegerField(null=True)),
                ('finished_subjects', models.IntegerField(null=True)),
                ('aborted_subjects', models.IntegerField(null=True)),
                ('SAE_count', models.PositiveIntegerField(default=0)),
                ('SUSAR_count', models.PositiveIntegerField(default=0)),
                ('runs_till', models.DateField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('notifications.notification',),
        ),
        migrations.CreateModel(
            name='SafetyNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.Notification')),
                ('safety_type', models.CharField(db_index=True, max_length=6, verbose_name='Type', choices=[(b'susar', 'SUSAR'), (b'sae', 'SAE'), (b'asr', 'Annual Safety Report'), (b'other', 'Other Safety Report')])),
                ('is_acknowledged', models.BooleanField(default=False)),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=('notifications.notification',),
        ),
        migrations.AddField(
            model_name='notificationanswer',
            name='notification',
            field=models.OneToOneField(related_name='answer', to='notifications.Notification'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationanswer',
            name='pdf_document',
            field=models.OneToOneField(related_name='_notification_answer', null=True, to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='documents',
            field=models.ManyToManyField(related_name='notifications', to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='pdf_document',
            field=models.OneToOneField(related_name='_notification', null=True, to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='submission_forms',
            field=models.ManyToManyField(related_name='notifications', to='core.SubmissionForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.ForeignKey(related_name='notifications', to='notifications.NotificationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
