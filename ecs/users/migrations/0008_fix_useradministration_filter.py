# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def fix_useradministration_filter(apps, schema_editor):
    UserSettings = apps.get_model('users', 'UserSettings')
    for us in UserSettings.objects.exclude(useradministration_filter='{}'):
        if 'groups' in us.useradministration_filter:
            groups = us.useradministration_filter['groups']
            if not isinstance(groups, list):
                us.useradministration_filter['groups'] = [
                    int(pk) for pk in groups.split(',') if pk
                ]
        if 'medical_categories' in us.useradministration_filter:
            medical_categories = us.useradministration_filter['medical_categories']
            if not isinstance(medical_categories, list):
                us.useradministration_filter['medical_categories'] = [
                    int(pk) for pk in medical_categories.split(',') if pk
                ]
        us.save(update_fields=['useradministration_filter'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_userprofile_is_expedited_reviewer'),
    ]

    operations = [
        migrations.RunPython(fix_useradministration_filter),
    ]
