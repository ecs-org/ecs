from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0003_uuidfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='docstashdata',
            name='stash_id',
            field=models.UUIDField(null=True),
        ),
        migrations.RunSQL('''
            update docstash_docstashdata set stash_id = old_stash::uuid;
        ''', ''),
        migrations.RemoveField(
            model_name='docstash',
            name='old_key',
        ),
        migrations.AlterField(
            model_name='docstash',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, serialize=False, primary_key=True),
        ),
        migrations.RenameField(
            model_name='docstashdata',
            old_name='stash_id',
            new_name='stash',
        ),
        migrations.AlterField(
            model_name='docstashdata',
            name='stash',
            field=models.ForeignKey(related_name='data', to='docstash.DocStash'),
        ),
        migrations.AlterUniqueTogether(
            name='docstashdata',
            unique_together={('version', 'stash')},
        ),
        migrations.RemoveField(
            model_name='docstashdata',
            name='old_stash',
        ),
    ]
