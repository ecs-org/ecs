# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('billing', '0001_initial'),
        ('core', '0002_auto_20151217_1249'),
        ('checklists', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='document',
            field=models.OneToOneField(related_name='invoice', null=True, to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='submissions',
            field=models.ManyToManyField(to='core.Submission'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='checklistpayment',
            name='checklists',
            field=models.ManyToManyField(to='checklists.Checklist'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='checklistpayment',
            name='document',
            field=models.OneToOneField(related_name='checklist_payment', null=True, to='documents.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='checklistbillingstate',
            name='checklist',
            field=models.OneToOneField(related_name='billing_state', null=True, to='checklists.Checklist'),
            preserve_default=True,
        ),
    ]
