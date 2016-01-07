from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            alter table notifications_notification
                alter column timestamp drop default;
        ''')
    ]
