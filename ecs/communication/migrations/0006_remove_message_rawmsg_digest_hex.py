from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0005_uuidfield'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='rawmsg_digest_hex',
        ),
    ]
