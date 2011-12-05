from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<submission_pk>\d+)/tasks/log/$', 'ecs.tasks.views.task_backlog'),
    url(r'^(?P<submission_pk>\d+)/messages/new/$', 'ecs.communication.views.new_thread'),
)

urlpatterns += patterns('ecs.core.views', 
    url(r'^list/all/$', 'all_submissions'),
    url(r'^list/assigned/$', 'assigned_submissions'),
    url(r'^list/mine/$', 'my_submissions'),
    url(r'^list/widget/$', 'submission_widget'),

    url(r'^import/$', 'import_submission_form'),
    url(r'^new/(?:(?P<docstash_key>.+)/)?$', 'create_submission_form'),
    url(r'^delete/(?P<docstash_key>.+)/$', 'delete_docstash_entry'),
    url(r'^doc/upload/(?P<docstash_key>.+)/$', 'upload_document_for_submission'),
    url(r'^doc/delete/(?P<docstash_key>.+)/$', 'delete_document_from_submission'),

    url(r'^diff/forms/(?P<old_submission_form_pk>\d+)/(?P<new_submission_form_pk>\d+)/$', 'diff'),

    url(r'^(?P<submission_pk>\d+)/$', 'view_submission', name='view_submission'),
    url(r'^(?P<submission_pk>\d+)/copy/$', 'copy_latest_submission_form'),
    url(r'^(?P<submission_pk>\d+)/export/$', 'export_submission'),
    url(r'^(?P<submission_pk>\d+)/presenter/change/$', 'change_submission_presenter'),
    url(r'^(?P<submission_pk>\d+)/susar_presenter/change/$', 'change_submission_susar_presenter'),

    url(r'^(?P<submission_pk>\d+)/temp-auth/grant/$', 'grant_temporary_access'),
    url(r'^(?P<submission_pk>\d+)/temp-auth/(?P<temp_auth_pk>\d+)/revoke/$', 'revoke_temporary_access'),

    url(r'^(?P<submission_form_pk>\d+)/task_delete/(?P<task_pk>\d+)/$', 'submissions.delete_task'),

    url(r'^form/(?P<submission_form_pk>\d+)/$', 'readonly_submission_form', name='readonly_submission_form'),
    url(r'^form/(?P<submission_form_pk>\d+)/pdf/$', 'submission_pdf'),
    url(r'^form/(?P<submission_form_pk>\d+)/copy/$', 'copy_submission_form'),
    url(r'^form/(?P<submission_form_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', 'copy_submission_form'),
    url(r'^form/(?P<submission_form_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/$', 'checklist_review'),
    url(r'^form/(?P<submission_form_pk>\d+)/review/checklist/show/(?P<checklist_pk>\d+)/$', 'show_checklist_review'),
    url(r'^form/(?P<submission_form_pk>\d+)/review/checklist/drop/(?P<checklist_pk>\d+)/$', 'drop_checklist_review'),
    url(r'^form/(?P<submission_form_pk>\d+)/review/categorization/$', 'categorization_review'),
    url(r'^form/(?P<submission_pk>\d+)/review/initial/$', 'initial_review'),
    url(r'^form/(?P<submission_pk>\d+)/review/paper_submission/$', 'paper_submission_review'),
    url(r'^form/(?P<submission_form_pk>\d+)/review/befangene/$', 'befangene_review'),
    url(r'^form/(?P<submission_form_pk>\d+)/review/vote/$', 'vote_review'),
    url(r'^form/(?P<submission_form_pk>\d+)/vote/prepare/$', 'vote_preparation'),
    url(r'^form/(?P<submission_form_pk>\d+)/vote/prepare/$', 'vote_preparation'),
    url(r'^form/(?P<submission_form_pk>\d+)/vote/b2-prepare/$', 'b2_vote_preparation'),
)
