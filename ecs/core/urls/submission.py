from django.conf import settings
from django.conf.urls import url

from ecs.core.views import submissions as views
from ecs.tasks.views import task_backlog, delete_task
from ecs.communication.views import new_thread


urlpatterns = (
    url(r'^(?P<submission_pk>\d+)/tasks/log/$', task_backlog),
    url(r'^(?P<submission_pk>\d+)/task/(?P<task_pk>\d+)/delete/$', delete_task),

    url(r'^(?P<submission_pk>\d+)/messages/new/$', new_thread),

    url(r'^list/all/$', views.all_submissions),
    url(r'^list/xls/$', views.xls_export),
    url(r'^list/xls/(?P<shasum>[0-9a-f]{40})/$', views.xls_export_download),
    url(r'^list/assigned/$', views.assigned_submissions),
    url(r'^list/mine/$', views.my_submissions),

    url(r'^import/$', views.import_submission_form),
    url(r'^new/(?:(?P<docstash_key>.+)/)?$', views.create_submission_form),
    url(r'^delete/(?P<docstash_key>.+)/$', views.delete_docstash_entry),
    url(r'^doc/upload/(?P<docstash_key>.+)/$', views.upload_document_for_submission),
    url(r'^doc/delete/(?P<docstash_key>.+)/$', views.delete_document_from_submission),

    url(r'^diff/forms/(?P<old_submission_form_pk>\d+)/(?P<new_submission_form_pk>\d+)/$', views.diff),

    url(r'^(?P<submission_pk>\d+)/$', views.view_submission, name='view_submission'),
    url(r'^(?P<submission_pk>\d+)/copy/$', views.copy_latest_submission_form),
    url(r'^(?P<submission_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', views.copy_latest_submission_form),
    url(r'^(?P<submission_pk>\d+)/export/$', views.export_submission),
    url(r'^(?P<submission_pk>\d+)/presenter/change/$', views.change_submission_presenter),
    url(r'^(?P<submission_pk>\d+)/susar_presenter/change/$', views.change_submission_susar_presenter),

    url(r'^(?P<submission_pk>\d+)/temp-auth/grant/$', views.grant_temporary_access),
    url(r'^(?P<submission_pk>\d+)/temp-auth/(?P<temp_auth_pk>\d+)/revoke/$', views.revoke_temporary_access),

    url(r'^form/(?P<submission_form_pk>\d+)/$', views.readonly_submission_form, name='readonly_submission_form'),
    url(r'^form/(?P<submission_form_pk>\d+)/pdf/$', views.submission_form_pdf),
    url(r'^form/(?P<submission_form_pk>\d+)/pdf/view/$', views.submission_form_pdf_view),
    url(r'^form/(?P<submission_form_pk>\d+)/doc/(?P<document_pk>\d+)/$', views.download_document),
    url(r'^form/(?P<submission_form_pk>\d+)/doc/(?P<document_pk>\d+)/view/$', views.view_document),
    url(r'^form/(?P<submission_form_pk>\d+)/copy/$', views.copy_submission_form),
    url(r'^form/(?P<submission_form_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', views.copy_submission_form),
    url(r'^form/(?P<submission_form_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/$', views.checklist_review),
    url(r'^form/(?P<submission_form_pk>\d+)/review/checklist/show/(?P<checklist_pk>\d+)/$', views.show_checklist_review),
    url(r'^form/(?P<submission_form_pk>\d+)/review/checklist/drop/(?P<checklist_pk>\d+)/$', views.drop_checklist_review),
    url(r'^(?P<submission_pk>\d+)/categorization/$', views.categorization),
    url(r'^(?P<submission_pk>\d+)/categorization/reopen/$', views.reopen_categorization),
    url(r'^(?P<submission_pk>\d+)/review/categorization/$', views.categorization_review),
    url(r'^form/(?P<submission_pk>\d+)/review/initial/$', views.initial_review),
    url(r'^form/(?P<submission_pk>\d+)/review/paper_submission/$', views.paper_submission_review),
    url(r'^form/(?P<submission_pk>\d+)/biased/$', views.biased_board_members),
    url(r'^form/(?P<submission_pk>\d+)/biased/remove/(?P<user_pk>\d+)/$', views.remove_biased_board_member),
    url(r'^form/(?P<submission_form_pk>\d+)/review/vote/$', views.vote_review),
    url(r'^form/(?P<submission_form_pk>\d+)/vote/prepare/$', views.vote_preparation),
    url(r'^form/(?P<submission_form_pk>\d+)/vote/prepare/$', views.vote_preparation),
    url(r'^form/(?P<submission_form_pk>\d+)/vote/b2-prepare/$', views.b2_vote_preparation),
)

if settings.DEBUG:
    urlpatterns += (
        url(r'^form/(?P<submission_form_pk>\d+)/pdf/debug/$', views.submission_form_pdf_debug),
    )
