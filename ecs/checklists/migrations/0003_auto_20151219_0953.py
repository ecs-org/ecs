from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0002_auto_20151217_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='status',
            field=models.CharField(default='new', max_length=15, choices=[('new', 'New'), ('completed', 'Completed'), ('review_ok', 'Review OK'), ('review_fail', 'Review Failed'), ('dropped', 'Dropped')]),
            preserve_default=True,
        ),
    ]
