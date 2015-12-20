# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Checklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'new', max_length=15, choices=[(b'new', 'Neu'), (b'completed', 'Abgeschlossen'), (b'review_ok', '\xdcberpr\xfcfung OK'), (b'review_fail', '\xdcberpr\xfcfung fehlgeschlagen'), (b'dropped', 'Fallengelassen')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChecklistAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.NullBooleanField()),
                ('comment', models.TextField(null=True, blank=True)),
                ('checklist', models.ForeignKey(related_name='answers', to='checklists.Checklist')),
            ],
            options={
                'ordering': ('question__blueprint', 'question__index'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChecklistBlueprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.CharField(unique=True, max_length=50, db_index=True)),
                ('multiple', models.BooleanField(default=False)),
                ('billing_required', models.BooleanField(default=False)),
                ('reviewer_is_anonymous', models.BooleanField(default=False)),
                ('allow_pdf_download', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChecklistQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=5, db_index=True)),
                ('index', models.IntegerField(db_index=True)),
                ('text', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=500, null=True, blank=True)),
                ('link', models.CharField(max_length=100, null=True, blank=True)),
                ('is_inverted', models.BooleanField(default=False)),
                ('requires_comment', models.BooleanField(default=False)),
                ('blueprint', models.ForeignKey(related_name='questions', to='checklists.ChecklistBlueprint')),
            ],
            options={
                'ordering': ('blueprint', 'index'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='checklistquestion',
            unique_together=set([('blueprint', 'number')]),
        ),
        migrations.AddField(
            model_name='checklistanswer',
            name='question',
            field=models.ForeignKey(to='checklists.ChecklistQuestion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='checklist',
            name='blueprint',
            field=models.ForeignKey(related_name='checklists', to='checklists.ChecklistBlueprint'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='checklist',
            name='last_edited_by',
            field=models.ForeignKey(related_name='edited_checklists', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
