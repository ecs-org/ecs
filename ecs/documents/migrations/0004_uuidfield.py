# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_deduplicate_downloadhistory_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='uuid',
            new_name='old_uuid',
        ),
        migrations.RenameField(
            model_name='downloadhistory',
            old_name='uuid',
            new_name='old_uuid',
        ),
        migrations.AddField(
            model_name='document',
            name='uuid',
            field=models.UUIDField(unique=True, null=True),
        ),
        migrations.AddField(
            model_name='downloadhistory',
            name='uuid',
            field=models.UUIDField(unique=True, null=True),
        ),
        migrations.RunSQL('''
            update documents_document set uuid = old_uuid::uuid;
            update documents_downloadhistory set uuid = old_uuid::uuid;
        '''),
        migrations.AlterField(
            model_name='document',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='downloadhistory',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, db_index=True),
        ),
        migrations.RemoveField(
            model_name='document',
            name='old_uuid',
        ),
        migrations.RemoveField(
            model_name='downloadhistory',
            name='old_uuid',
        ),
    ]
