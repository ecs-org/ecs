# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_pki(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            select count(*) from information_schema.columns
            where table_name='pki_certificate' and column_name = 'fingerprint'
        ''')
        if cursor.fetchone()[0]:
            cursor.execute('''
                create table pki_certificateauthority (
                    id serial primary key,
                    "key" text not null,
                    cert text not null
                );

                truncate pki_certificate;
                alter table pki_certificate
                    drop column fingerprint,
                    drop column is_revoked,
                    add column serial integer not null,
                    add column created_at timestamp with time zone not null,
                    add column expires_at timestamp with time zone not null,
                    add column revoked_at timestamp with time zone;

                alter table pki_certificate
                    add constraint pki_certificate_cn_uniq unique (cn);

                alter table pki_certificate
                    add constraint pki_certificate_serial_uniq unique (serial);
            ''')


class Migration(migrations.Migration):

    dependencies = [
        ('pki', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_pki),
    ]
