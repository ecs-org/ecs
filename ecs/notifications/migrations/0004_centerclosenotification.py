# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge'),
        ('notifications', '0003_auto_20160314_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='CenterCloseNotification',
            fields=[
                ('notification_ptr', models.OneToOneField(parent_link=True, to='notifications.Notification', serialize=False, auto_created=True, primary_key=True)),
                ('investigator', models.ForeignKey(to='core.Investigator', related_name='closed_by_notification')),
                ('close_date', models.DateField()),
            ],
            bases=('notifications.notification',),
        ),
    ]
