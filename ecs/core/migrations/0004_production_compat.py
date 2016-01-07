from django.db import models, migrations


def add_django_session_index(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("select to_regclass('django_session_expire_date')")
        if not cursor.fetchone()[0]:
            cursor.execute('''
                create index "django_session_expire_date" on "django_session" ("expire_date");
            ''')


def remove_bugshot_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')

    try:
        bugshot_group = Group.objects.get(name='bugshot')
    except Group.DoesNotExist:
        pass
    else:
        bugshot_group.user_set = []
        bugshot_group.save()
        bugshot_group.delete()


def migrate_reversion_tables(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            select count(*) from information_schema.columns
            where table_name='reversion_version' and column_name = 'object_id_int'
        ''')
        if not cursor.fetchone()[0]:
            cursor.execute('''
                alter table reversion_version add column object_id_int integer;
                create index reversion_version_0c9ba3a3
                    on reversion_version using btree (object_id_int);
                update reversion_version set object_id_int = object_id::integer;
                alter table reversion_revision add column manager_slug varchar(200);
                update reversion_revision set manager_slug = 'default';
                alter table reversion_revision alter column manager_slug set not null;
                create index reversion_revision_b16b0f06
                    on reversion_revision using btree (manager_slug);
                create index reversion_revision_manager_slug_54d21219582503b1_like
                    on reversion_revision using btree (manager_slug varchar_pattern_ops);
                create index reversion_revision_c69e55a4
                    on reversion_revision using btree (date_created);
            ''')


def remove_default_from_boolean_fields(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            select column_default from information_schema.columns
            where table_name='checklists_checklistblueprint' and
                column_name = 'multiple'
        ''')
        if cursor.fetchone()[0] is not None:
            cursor.execute('''
                alter table checklists_checklistblueprint
                    alter column multiple drop default;

                alter table communication_message
                    alter column unread drop default,
                    alter column soft_bounced drop default,
                    alter column origin drop default,
                    alter column smtp_delivery_state drop default,
                    alter column uuid drop default;

                alter table communication_thread
                    alter column closed_by_sender drop default,
                    alter column closed_by_receiver drop default;

                alter table core_investigator
                    alter column main drop default,
                    alter column jus_practicandi drop default,
                    alter column certified drop default;

                alter table core_submissionform
                    alter column is_acknowledged drop default,
                    alter column submission_type drop default,
                    alter column sponsor_agrees_to_publishing drop default,
                    alter column project_type_non_reg_drug drop default,
                    alter column project_type_reg_drug drop default,
                    alter column project_type_reg_drug_within_indication drop default,
                    alter column project_type_reg_drug_not_within_indication drop default,
                    alter column project_type_medical_method drop default,
                    alter column project_type_medical_device drop default,
                    alter column project_type_medical_device_with_ce drop default,
                    alter column project_type_medical_device_without_ce drop default,
                    alter column project_type_medical_device_performance_evaluation drop default,
                    alter column project_type_basic_research drop default,
                    alter column project_type_genetic_study drop default,
                    alter column project_type_register drop default,
                    alter column project_type_biobank drop default,
                    alter column project_type_retrospective drop default,
                    alter column project_type_questionnaire drop default,
                    alter column project_type_psychological_study drop default,
                    alter column already_voted drop default,
                    alter column subject_noncompetents drop default,
                    alter column subject_males drop default,
                    alter column subject_females drop default,
                    alter column subject_childbearing drop default,
                    alter column study_plan_observer_blinded drop default,
                    alter column study_plan_randomized drop default,
                    alter column study_plan_parallelgroups drop default,
                    alter column study_plan_controlled drop default,
                    alter column study_plan_cross_over drop default,
                    alter column study_plan_placebo drop default,
                    alter column study_plan_factorized drop default,
                    alter column study_plan_pilot_project drop default,
                    alter column study_plan_equivalence_testing drop default,
                    alter column study_plan_population_intention_to_treat drop default,
                    alter column study_plan_population_per_protocol drop default,
                    alter column submitter_is_coordinator drop default,
                    alter column submitter_is_main_investigator drop default,
                    alter column submitter_is_sponsor drop default,
                    alter column submitter_is_authorized_by_sponsor drop default;

                alter table docstash_docstash
                    alter column current_version drop default;

                alter table documents_document
                    alter column mimetype drop default;

                alter table documents_documenttype
                    alter column identifier drop default,
                    alter column helptext drop default;

                alter table meetings_constraint
                    alter column weight drop default;

                alter table meetings_timetableentry
                    alter column is_break drop default,
                    alter column is_open drop default;

                alter table notifications_completionreportnotification
                    alter column "SAE_count" drop default,
                    alter column "SUSAR_count" drop default,
                    alter column study_aborted drop default;

                alter table notifications_notification
                    alter column comments drop default;

                alter table notifications_notificationtype
                    alter column form drop default;

                alter table notifications_progressreportnotification
                    alter column "SAE_count" drop default,
                    alter column "SUSAR_count" drop default;

                alter table tasks_task
                    alter column accepted drop default;

                alter table users_invitation
                    alter column uuid drop default,
                    alter column is_accepted drop default;

                alter table users_userprofile
                    alter column is_phantom drop default,
                    alter column is_indisposed drop default,
                    alter column is_board_member drop default,
                    alter column is_executive_board_member drop default,
                    alter column is_thesis_reviewer drop default,
                    alter column is_insurance_reviewer drop default,
                    alter column is_expedited_reviewer drop default,
                    alter column is_internal drop default,
                    alter column single_login_enforced drop default;

                alter table votes_vote
                    alter column is_final_version drop default;

                alter table workflow_edge
                    alter column deadline drop default,
                    alter column negated drop default;

                alter table workflow_graph
                    alter column auto_start drop default;

                alter table workflow_node
                    alter column is_start_node drop default,
                    alter column is_end_node drop default;

                alter table workflow_token
                    alter column locked drop default;

                alter table workflow_workflow
                    alter column is_finished drop default;
            ''')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151217_1249'),
        ('reversion', '0001_initial'),
        ('sessions', '0001_initial'),
        ('documents', '0002_production_compat'),
        ('boilerplate', '0002_production_compat'),
        ('communication', '0004_production_compat'),
        ('docstash', '0002_production_compat'),
        ('notifications', '0002_production_compat'),
        ('pki', '0002_production_compat'),
        ('tracking', '0002_production_compat'),
        ('users', '0002_production_compat'),
    ]

    operations = [
        migrations.RunPython(add_django_session_index),
        migrations.RunPython(remove_bugshot_group),
        migrations.RunPython(migrate_reversion_tables),
        migrations.RunPython(remove_default_from_boolean_fields),
        migrations.RunSQL('''
            -- remove old pdfviewer document annotations
            drop table if exists pdfviewer_documentannotation;

            -- remove sentry tables
            drop table if exists sentry_filtervalue;
            drop table if exists sentry_message;
            drop table if exists sentry_messagecountbyminute;
            drop table if exists sentry_messagefiltervalue;
            drop table if exists sentry_messageindex;
            drop table if exists sentry_groupedmessage;

            -- remove dbtemplates tables
            drop table if exists django_template_sites;
            drop table if exists django_template;

            -- remove old auth messgaes
            drop table if exists auth_message;

            -- remove south bookkeeping table
            drop table if exists south_migrationhistory;

            -- remove old feedback table
            drop table if exists feedback_feedback;

            -- remove old indexer table
            drop table if exists indexer_index;
        '''),
    ]
