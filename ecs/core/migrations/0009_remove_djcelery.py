from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_uuidfield'),
    ]

    operations = [
        migrations.RunSQL('''
            drop table
                djcelery_crontabschedule,
                djcelery_intervalschedule,
                djcelery_periodictask,
                djcelery_periodictasks,
                djcelery_taskstate,
                djcelery_workerstate;
        ''')
    ]
