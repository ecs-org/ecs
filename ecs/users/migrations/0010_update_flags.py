# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_flags(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    for u in User.objects.all():
        groups = set(u.groups.values_list('name', flat=True))
        u.profile.is_internal = bool(groups & {
            'EC-Office',
            'EC-Internal Reviewer',
            'EC-Executive Board Member',
            'EC-Signing',
            'EC-Notification Reviewer',
            'EC-Thesis Review Group',
            'EC-Thesis Executive Group',
            'EC-B2 Reviewer',
            'EC-Paper Submission Reviewer',
            'EC-Safety Report Reviewer',
            'Local-EC Reviewer',
            'EC-Vote Preparation',
            'External Review Reviewer',
        })
        u.profile.has_explicit_workflow = bool(groups - {
            'External Reviewer',
            'Userswitcher Target',
            'Amendment Receiver',
            'Meeting Protocol Receiver',
        })
        u.profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_userprofile_is_developer'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='has_explicit_workflow',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(update_flags),
    ]
