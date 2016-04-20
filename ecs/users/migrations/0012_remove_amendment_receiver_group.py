# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def remove_amendment_receiver_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    try:
        g = Group.objects.get(name='Amendment Receiver')
    except Group.DoesNotExist:
        return

    assert(g.user_set.count() == 0)
    g.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_userprofile_is_help_writer'),
    ]

    operations = [
        migrations.RunPython(remove_amendment_receiver_group),
    ]
