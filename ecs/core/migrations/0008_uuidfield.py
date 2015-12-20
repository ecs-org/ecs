# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20151219_1425'),
    ]

    operations = [
        migrations.RunSQL('''
            update core_ethicscommission
                set uuid = 'c890205dcb7543c8a76bf324512c5f81'
                where uuid = 'c890205dcb7543c8a76b-324512c5f81';
        '''),
        migrations.RenameField(
            model_name='ethicscommission',
            old_name='uuid',
            new_name='old_uuid',
        ),
        migrations.AddField(
            model_name='ethicscommission',
            name='uuid',
            field=models.UUIDField(unique=True, null=True),
        ),
        migrations.RunSQL('''
            update core_ethicscommission set uuid = old_uuid::uuid;
        '''),
        migrations.AlterField(
            model_name='ethicscommission',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.RemoveField(
            model_name='ethicscommission',
            name='old_uuid',
        ),
    ]
