from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0002_production_compat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='ip',
            field=models.GenericIPAddressField(protocol='ipv4', db_index=True),
            preserve_default=True,
        ),
    ]
