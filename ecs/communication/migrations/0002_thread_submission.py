from django.db import models, migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communication', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='submission',
            field=models.ForeignKey(to='core.Submission', null=True),
            preserve_default=True,
        ),
    ]
