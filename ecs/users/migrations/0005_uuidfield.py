from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_userprofile_start_workflow'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitation',
            old_name='uuid',
            new_name='old_uuid',
        ),
        migrations.AddField(
            model_name='invitation',
            name='uuid',
            field=models.UUIDField(unique=True, null=True),
        ),
        migrations.RunSQL('''
            update users_invitation set uuid = old_uuid::uuid;
        '''),
        migrations.AlterField(
            model_name='invitation',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, db_index=True),
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='old_uuid',
        ),
    ]
