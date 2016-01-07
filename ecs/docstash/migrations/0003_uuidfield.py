from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0002_production_compat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='docstash',
            old_name='key',
            new_name='old_key',
        ),
        migrations.AddField(
            model_name='docstash',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, serialize=False),
        ),
        migrations.AlterField(
            model_name='docstashdata',
            name='stash',
            field=models.CharField(max_length=41),
        ),
        migrations.RenameField(
            model_name='docstashdata',
            old_name='stash',
            new_name='old_stash',
        ),
        migrations.RunSQL('update docstash_docstash set key = old_key::uuid'),
    ]
