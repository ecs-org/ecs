# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ethicscommission',
            name='address_1',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='address_2',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='chairperson',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='city',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='contactname',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='email',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='fax',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='url',
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='zip_code',
        ),
    ]
