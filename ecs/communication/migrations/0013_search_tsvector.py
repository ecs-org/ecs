# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('communication', '0012_auto_20170116_1344'),
        ('core', '0044_auto_20170203_1351'),
    ]

    operations = [
        migrations.RunSQL('''
            alter table communication_thread
            add column searchvector tsvector;

            with m as (
                select
                    m.thread_id,
                    string_agg(m.text, ' ') as text,
                    string_agg(concat_ws(' ',
                        sender.first_name, sender.last_name, sender.email,
                        receiver.first_name, receiver.last_name, receiver.email
                    ), ' ') as users
                from communication_message m
                inner join auth_user sender on sender.id = m.sender_id
                inner join auth_user receiver on receiver.id = m.receiver_id
                group by m.thread_id
            ), s as (
                select t.id as thread_id, s.ec_number
                from communication_thread t
                left join core_submission s on s.id = t.submission_id
            )
            update communication_thread t
            set searchvector =
                setweight(to_tsvector('german',
                    concat_ws(' ',
                        t.subject,
                        concat_ws('/', s.ec_number % 10000, s.ec_number / 10000)
                    )
                ), 'A') ||
                setweight(to_tsvector('german', concat_ws(' ', m.text, m.users)), 'B')
            from m, s
            where m.thread_id = t.id and s.thread_id = t.id;

            alter table communication_thread
            alter column searchvector set not null;

            create function communication_thread_set_searchvector() returns trigger as $$
            begin
                new.searchvector = setweight(to_tsvector('german', new.subject), 'A');
                if new.submission_id is not null then
                    new.searchvector = new.searchvector || (
                        select setweight(to_tsvector('german',
                            concat_ws('/', ec_number % 10000, ec_number / 10000)), 'A')
                        from core_submission
                        where id = new.submission_id
                    );
                end if;
                return new;
            end
            $$ language plpgsql;

            create trigger communication_thread_search_trigger before insert
            on communication_thread for each row
            execute procedure communication_thread_set_searchvector();

            create function communication_message_update_searchvector() returns trigger as $$
            declare
                sender auth_user%rowtype;
                receiver auth_user%rowtype;
            begin
                select * into sender from auth_user where id = new.sender_id;
                select * into receiver from auth_user where id = new.receiver_id;

                update communication_thread t
                set searchvector = t.searchvector ||
                    setweight(to_tsvector('german',
                        concat_ws(' ',
                            new.text,
                            sender.first_name, sender.last_name, sender.email,
                            receiver.first_name, receiver.last_name, receiver.email
                        )
                    ), 'B')
                where t.id = new.thread_id;

                return new;
            end
            $$ language plpgsql;

            create trigger communication_message_search_trigger before insert
            on communication_message for each row
            execute procedure communication_message_update_searchvector();

            create index communication_thread_searchvector_idx
            on communication_thread using gin (searchvector);
        ''', '''
            drop trigger communication_thread_search_trigger on communication_thread;
            drop function communication_thread_set_searchvector();
            drop trigger communication_message_search_trigger on communication_message;
            drop function communication_message_update_searchvector();
            drop index communication_thread_searchvector_idx;
            alter table communication_thread drop column searchvector;
        '''),
    ]
