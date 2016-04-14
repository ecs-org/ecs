# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_help_writer_group(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    help_writer_group, _ = Group.objects.get_or_create(name='Help Writer')

    for u in User.objects.all():
        if u.profile.is_help_writer:
            u.groups.add(help_writer_group)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_update_flags'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(add_help_writer_group),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_help_writer',
        ),
    ]
