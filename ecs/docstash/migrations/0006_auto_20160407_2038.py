# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('docstash', '0005_fix_2to3'),
    ]

    operations = [
        migrations.AddField(
            model_name='docstash',
            name='modtime',
            field=models.DateTimeField(null=True, auto_now=True),
        ),
        migrations.AddField(
            model_name='docstash',
            name='name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='docstash',
            name='value',
            field=picklefield.fields.PickledObjectField(default=dict, editable=False),
        ),
        migrations.RunSQL('''
            update docstash_docstash stash
                set (modtime, name, value) =
                    (data.modtime, data.name, data.value)
                from docstash_docstashdata data
                where stash.key = data.stash_id and
                    stash.current_version = data.version;

            delete from docstash_docstash where current_version = -1;

            set constraints all immediate;
        '''),
        migrations.AlterField(
            model_name='docstash',
            name='modtime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='docstashdata',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='docstashdata',
            name='stash',
        ),
        migrations.DeleteModel(
            name='DocStashData',
        ),
    ]
