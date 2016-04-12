# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def group_cleanup(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    try:
        group = Group.objects.get(name='translators')
    except Group.DoesNotExist:
        pass
    else:
        group.user_set.clear()
        group.delete()

    Group.objects.filter(name='userswitcher_target').update(name='Userswitcher Target')
    Group.objects.filter(name='EC-Internal Review Group').update(name='EC-Internal Reviewer')
    Group.objects.filter(name='EC-Executive Board Group').update(name='EC-Executive Board Member')
    Group.objects.filter(name='EC-Signing Group').update(name='EC-Signing')
    Group.objects.filter(name='EC-Statistic Group').update(name='EC-Statistic Reviewer')
    Group.objects.filter(name='EC-Notification Review Group').update(name='EC-Notification Reviewer')
    Group.objects.filter(name='EC-B2 Review Group').update(name='EC-B2 Reviewer')
    Group.objects.filter(name='EC-Paper Submission Review Group').update(name='EC-Paper Submission Reviewer')
    Group.objects.filter(name='EC-Safety Report Review Group').update(name='EC-Safety Report Reviewer')
    Group.objects.filter(name='Local-EC Review Group').update(name='Local-EC Reviewer')
    Group.objects.filter(name='GCP Review Group').update(name='GCP Reviewer')
    Group.objects.filter(name='External Review Review Group').update(name='External Review Reviewer')
    Group.objects.filter(name='EC-Vote Preparation Group').update(name='EC-Vote Preparation')
    Group.objects.filter(name='Amendment Receiver Group').update(name='Amendment Receiver')
    Group.objects.filter(name='Meeting Protocol Receiver Group').update(name='Meeting Protocol Receiver')
    Group.objects.filter(name='Resident Board Member Group').update(name='Resident Board Member')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_userprofile_is_expedited_reviewer'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(group_cleanup),
    ]
