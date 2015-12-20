# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(unique=True, max_length=32)),
                ('is_accepted', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='ecs_invitations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoginHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=32, choices=[(b'login', 'login'), (b'logout', 'logout')])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip', models.IPAddressField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_password_change', models.DateTimeField(auto_now_add=True)),
                ('is_phantom', models.BooleanField(default=False)),
                ('is_indisposed', models.BooleanField(default=False)),
                ('start_workflow', models.BooleanField(default=False)),
                ('is_board_member', models.BooleanField(default=False)),
                ('is_executive_board_member', models.BooleanField(default=False)),
                ('is_thesis_reviewer', models.BooleanField(default=False)),
                ('is_insurance_reviewer', models.BooleanField(default=False)),
                ('is_expedited_reviewer', models.BooleanField(default=False)),
                ('is_internal', models.BooleanField(default=False)),
                ('is_resident_member', models.BooleanField(default=False)),
                ('is_help_writer', models.BooleanField(default=False)),
                ('is_testuser', models.BooleanField(default=False)),
                ('is_developer', models.BooleanField(default=False)),
                ('session_key', models.CharField(max_length=40, null=True)),
                ('single_login_enforced', models.BooleanField(default=False)),
                ('gender', models.CharField(max_length=1, choices=[(b'f', 'Ms'), (b'm', 'Mr')])),
                ('title', models.CharField(max_length=30, blank=True)),
                ('organisation', models.CharField(max_length=180, blank=True)),
                ('jobtitle', models.CharField(max_length=130, blank=True)),
                ('swift_bic', models.CharField(max_length=11, blank=True)),
                ('iban', models.CharField(max_length=40, blank=True)),
                ('address1', models.CharField(max_length=60, blank=True)),
                ('address2', models.CharField(max_length=60, blank=True)),
                ('zip_code', models.CharField(max_length=10, blank=True)),
                ('city', models.CharField(max_length=80, blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('fax', models.CharField(max_length=45, blank=True)),
                ('social_security_number', models.CharField(max_length=10, blank=True)),
                ('forward_messages_after_minutes', models.PositiveIntegerField(default=0)),
                ('communication_proxy', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submission_filter_search', django_extensions.db.fields.json.JSONField()),
                ('submission_filter_all', django_extensions.db.fields.json.JSONField()),
                ('submission_filter_widget', django_extensions.db.fields.json.JSONField()),
                ('submission_filter_widget_internal', django_extensions.db.fields.json.JSONField()),
                ('submission_filter_mine', django_extensions.db.fields.json.JSONField()),
                ('submission_filter_assigned', django_extensions.db.fields.json.JSONField()),
                ('task_filter', models.TextField(null=True)),
                ('communication_filter', django_extensions.db.fields.json.JSONField()),
                ('useradministration_filter', django_extensions.db.fields.json.JSONField()),
                ('user', models.OneToOneField(related_name='ecs_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
