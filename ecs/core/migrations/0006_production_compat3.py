from django.db import models, migrations


def upgrade_celery_tables(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("select to_regclass('celery_taskmeta_task_id_like')")
        if cursor.fetchone()[0]:
            cursor.execute('''
                TRUNCATE djcelery_crontabschedule, djcelery_intervalschedule,
                    djcelery_periodictask, djcelery_periodictasks,
                    djcelery_taskstate, djcelery_workerstate, celery_taskmeta,
                    celery_tasksetmeta;

                ALTER TABLE djcelery_periodictask
                    DROP CONSTRAINT djcelery_periodictask_crontab_id_fkey;

                ALTER TABLE djcelery_periodictask
                    DROP CONSTRAINT djcelery_periodictask_interval_id_fkey;

                ALTER TABLE djcelery_taskstate
                    DROP CONSTRAINT djcelery_taskstate_worker_id_fkey;

                DROP INDEX celery_taskmeta_task_id_like;
                DROP INDEX celery_tasksetmeta_taskset_id_like;
                DROP INDEX djcelery_periodictask_crontab_id;
                DROP INDEX djcelery_periodictask_interval_id;
                DROP INDEX djcelery_periodictask_name_like;
                DROP INDEX djcelery_taskstate_hidden;
                DROP INDEX djcelery_taskstate_name;
                DROP INDEX djcelery_taskstate_name_like;
                DROP INDEX djcelery_taskstate_state;
                DROP INDEX djcelery_taskstate_state_like;
                DROP INDEX djcelery_taskstate_task_id_like;
                DROP INDEX djcelery_taskstate_tstamp;
                DROP INDEX djcelery_taskstate_worker_id;
                DROP INDEX djcelery_workerstate_hostname_like;
                DROP INDEX djcelery_workerstate_last_heartbeat;

                ALTER TABLE celery_taskmeta
                    ADD COLUMN hidden boolean NOT NULL,
                    ADD COLUMN meta text;

                ALTER TABLE celery_tasksetmeta
                    ADD COLUMN hidden boolean NOT NULL;

                ALTER TABLE djcelery_crontabschedule
                    ADD COLUMN day_of_month character varying(64) NOT NULL,
                    ADD COLUMN month_of_year character varying(64) NOT NULL;

                ALTER TABLE djcelery_periodictask
                    ADD COLUMN description text NOT NULL;

                ALTER TABLE djcelery_periodictask
                    ADD CONSTRAINT dj_interval_id_20cfc1cad060dfad_fk_djcelery_intervalschedule_id FOREIGN KEY (interval_id) REFERENCES djcelery_intervalschedule(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE djcelery_periodictask
                    ADD CONSTRAINT djce_crontab_id_1d8228f5b44b680a_fk_djcelery_crontabschedule_id FOREIGN KEY (crontab_id) REFERENCES djcelery_crontabschedule(id) DEFERRABLE INITIALLY DEFERRED;

                ALTER TABLE djcelery_taskstate
                    ADD CONSTRAINT djcelery__worker_id_30050731b1c3d3d9_fk_djcelery_workerstate_id FOREIGN KEY (worker_id) REFERENCES djcelery_workerstate(id) DEFERRABLE INITIALLY DEFERRED;

                CREATE INDEX celery_taskmeta_662f707d ON celery_taskmeta USING btree (hidden);

                CREATE INDEX celery_taskmeta_task_id_1efd6ed1da631331_like ON celery_taskmeta USING btree (task_id varchar_pattern_ops);

                CREATE INDEX celery_tasksetmeta_662f707d ON celery_tasksetmeta USING btree (hidden);

                CREATE INDEX celery_tasksetmeta_taskset_id_24b26c359742c9ab_like ON celery_tasksetmeta USING btree (taskset_id varchar_pattern_ops);

                CREATE INDEX djcelery_periodictask_1dcd7040 ON djcelery_periodictask USING btree (interval_id);

                CREATE INDEX djcelery_periodictask_f3f0d72a ON djcelery_periodictask USING btree (crontab_id);

                CREATE INDEX djcelery_periodictask_name_47c621f8dc029d22_like ON djcelery_periodictask USING btree (name varchar_pattern_ops);

                CREATE INDEX djcelery_taskstate_662f707d ON djcelery_taskstate USING btree (hidden);

                CREATE INDEX djcelery_taskstate_863bb2ee ON djcelery_taskstate USING btree (tstamp);

                CREATE INDEX djcelery_taskstate_9ed39e2e ON djcelery_taskstate USING btree (state);

                CREATE INDEX djcelery_taskstate_b068931c ON djcelery_taskstate USING btree (name);

                CREATE INDEX djcelery_taskstate_ce77e6ef ON djcelery_taskstate USING btree (worker_id);

                CREATE INDEX djcelery_taskstate_name_4337b4449e8827d_like ON djcelery_taskstate USING btree (name varchar_pattern_ops);

                CREATE INDEX djcelery_taskstate_state_19cb9b39780e399c_like ON djcelery_taskstate USING btree (state varchar_pattern_ops);

                CREATE INDEX djcelery_taskstate_task_id_29366bc6dcd6fd60_like ON djcelery_taskstate USING btree (task_id varchar_pattern_ops);

                CREATE INDEX djcelery_workerstate_f129901a ON djcelery_workerstate USING btree (last_heartbeat);

                CREATE INDEX djcelery_workerstate_hostname_3900851044588416_like ON djcelery_workerstate USING btree (hostname varchar_pattern_ops);
            ''')


def migrate_countries2(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("select to_regclass('submission_registered_countries')")
        if cursor.fetchone()[0]:
            cursor.execute('''
                alter table core_submissionform
                    alter column substance_p_c_t_countries set not null,
                    alter column substance_registered_in_countries set not null;

                drop table core_submissionform_substance_p_c_t_countries;
                drop table submission_registered_countries;
                drop table country;
                drop table usstate;
            ''')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_production_compat2'),
    ]

    operations = [
        migrations.RunPython(upgrade_celery_tables),
        migrations.RunPython(migrate_countries2),
    ]
