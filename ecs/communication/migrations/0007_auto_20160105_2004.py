from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0006_remove_message_rawmsg_digest_hex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='smtp_delivery_state',
            field=models.CharField(default='new', max_length=7, db_index=True, choices=[('new', 'new'), ('started', 'started'), ('success', 'success'), ('failure', 'failure')]),
        ),
    ]
