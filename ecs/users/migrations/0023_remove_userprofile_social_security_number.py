# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_userprofile_signing_connector'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='social_security_number',
        ),
    ]

