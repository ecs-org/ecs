# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import migrations, models
from django.conf import settings


def file2content(apps, schema_editor):
    ECSHELP_ROOT = os.path.join(settings.PROJECT_DIR, '..', 'ecs-help', 'images')
    Attachment = apps.get_model('help', 'Attachment')

    for attachment in Attachment.objects.all():
        path = os.path.join(ECSHELP_ROOT, attachment.slug)
        with open(path, 'rb') as f:
            attachment.content = f.read()
        attachment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='content',
            field=models.BinaryField(null=True),
        ),
        migrations.RunPython(file2content),
        migrations.AlterField(
            model_name='attachment',
            name='content',
            field=models.BinaryField(),
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='file',
        ),
    ]
