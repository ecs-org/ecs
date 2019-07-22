# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0014_auto_reply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='outgoing_msgid',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
