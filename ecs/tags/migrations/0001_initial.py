# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_djcelery'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9._-]{1,25}$')])),
                ('color', models.IntegerField()),
                ('submissions', models.ManyToManyField(related_name='tags', to='core.Submission')),
            ],
        ),
    ]
