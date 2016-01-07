from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_production_compat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginhistory',
            name='ip',
            field=models.GenericIPAddressField(protocol='ipv4'),
            preserve_default=True,
        ),
    ]
