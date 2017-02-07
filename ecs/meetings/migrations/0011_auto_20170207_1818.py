# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0010_meeting_documents_zip'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meeting',
            old_name='expedited_reviewer_invitation_sent_for',
            new_name='deadline_expedited_review',
        ),
    ]
