from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
            alter table tracking_request alter column timestamp drop default;
        ''')
    ]
