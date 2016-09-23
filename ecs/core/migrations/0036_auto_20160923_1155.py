# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20160920_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsettings',
            name='vote1_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='vote2_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='vote3a_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='vote3b_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='vote4_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='vote5_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='vote_pdf_extra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunSQL('''
            update core_advancedsettings
                set (vote2_extra, vote3b_extra, vote_pdf_extra) = (
                    'Achtung: Die Ethik-Kommission ersucht um möglichst zeitnahe Nachreichung. Werden die geforderten Unterlagen nicht innerhalb von 2 Jahren (ab Datum dieser Sitzung) nachgereicht, gilt der Antrag als zurückgezogen und muss gegebenenfalls als Neuantrag eingereicht werden.',
                    'Achtung: Werden die geforderten Unterlagen von den Antragstellern nicht innerhalb von 2 Sitzungsperioden (ab Datum dieser Sitzung) nachgereicht, gilt der Antrag ohne weitere Benachrichtigung als zurückgezogen und muss gegebenenfalls als Neuantrag eingereicht werden.',
                    'ACHTUNG: Unter Berücksichtigung der "ICH-Guideline for Good Clinical Practice" gilt dieser Beschluss ein Jahr ab Datum der Ausstellung. Gegebenenfalls hat der Antragsteller eine Verlängerung der Gültigkeit rechtzeitig zu beantragen.'
                );
        '''),
    ]
