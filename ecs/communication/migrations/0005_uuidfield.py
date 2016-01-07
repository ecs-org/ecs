from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0004_production_compat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='uuid',
            new_name='old_uuid',
        ),
        migrations.AddField(
            model_name='message',
            name='uuid',
            field=models.UUIDField(unique=True, null=True),
        ),
        migrations.RunSQL('''
            update communication_message set uuid = old_uuid::uuid;
        '''),
        migrations.AlterField(
            model_name='message',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, db_index=True),
        ),
        migrations.RemoveField(
            model_name='message',
            name='old_uuid',
        ),
    ]
