from django.db import models, migrations


def migrate_documents(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            select count(*) from information_schema.columns
            where table_name='documents_document' and column_name = 'pages'
        ''')
        if cursor.fetchone()[0]:
            cursor.execute('''
                alter table documents_document
                    drop column pages,
                    drop column allow_download,
                    add column stamp_on_download boolean,
                    drop column hash,
                    drop column file,
                    drop column status,
                    drop column retries;

                update documents_document
                    set stamp_on_download = (branding in ('b', 'p'));

                alter table documents_document
                    alter column stamp_on_download set not null,
                    drop column branding;

                alter table documents_downloadhistory
                    add column uuid character varying(36),
                    add column context character varying(15);

                update documents_downloadhistory hist set uuid = doc.uuid, context = 'download'
                from documents_document doc where doc.id = hist.document_id;

                alter table documents_downloadhistory
                    alter column uuid set not null,
                    alter column context set not null;

                create index documents_downloadhistory_uuid
                    on documents_downloadhistory using btree (uuid);
                create index documents_downloadhistory_uuid_like
                    on documents_downloadhistory using btree (uuid varchar_pattern_ops);
            ''')


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_documents),
        migrations.RunSQL('''
            drop table if exists documents_page;
            drop table if exists documents_documentpersonalization;
        '''),
    ]
