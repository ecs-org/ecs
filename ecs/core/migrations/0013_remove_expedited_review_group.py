# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def remove_expedited_reviewer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    try:
        exp_g = Group.objects.get(name='Expedited Review Group')
    except Group.DoesNotExist:
        return

    bm_g = Group.objects.get(name='EC-Board Member')

    exp_g.user_set.clear()
    exp_g.permissions.clear()
    for tt in exp_g.task_types.all():
        tt.groups.remove(exp_g)
        tt.groups.add(bm_g)
    exp_g.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_submission_expedited_review_categories'),
        ('auth', '0001_initial'),
        ('users', '0007_remove_userprofile_is_expedited_reviewer'),
        ('tasks', '0003_merge_medical_categories'),
    ]

    operations = [
        migrations.RunPython(remove_expedited_reviewer_group),
    ]
