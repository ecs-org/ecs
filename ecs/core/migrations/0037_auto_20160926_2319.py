# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_auto_20160923_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedsettings',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='contact_email',
            field=models.EmailField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='contact_url',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='meeting_address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='member_list_url',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='advancedsettings',
            name='signature_block',
            field=models.TextField(null=True),
        ),
        migrations.RunSQL('''
            update core_advancedsettings
            set (
                address, meeting_address, contact_email, contact_url,
                member_list_url, signature_block
            ) = (
                E'Borschkegasse 8b/6\nA-1090 Wien, Austria',
                E'Sitzungssaal der Ethik-Kommission\nBorschkegasse 8b/6. Stock\n1090 Wien',
                'ethik-kom@meduniwien.ac.at',
                'http://ethikkommission.meduniwien.ac.at/',
                'http://ethikkommission.meduniwien.ac.at/ethik-kommission/mitglieder/',
                E'Mit freundlichen Grüßen,\n\ndas Team der Ethik-Kommission'
            );
        '''),
    ]
