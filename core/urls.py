from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/dashboard/', 'permanent': True}),
    url(r'^autocomplete/(?P<queryset_name>[^/]+)/$', 'ecs.core.views.autocomplete'),
    url(r'^autocomplete/internal/(?P<queryset_name>[^/]+)/$', 'ecs.core.views.internal_autocomplete'),
    url(r'^fieldhistory/(?P<model_name>[^/]+)/(?P<pk>\d+)/$', 'ecs.core.views.field_history'),

    url(r'^submission/(?P<submission_pk>\d+)/$', 'ecs.core.views.view_submission'),
    url(r'^submission/(?P<submission_pk>\d+)/copy_form/$', 'ecs.core.views.copy_latest_submission_form'),
    url(r'^submission/(?P<submission_pk>\d+)/messages/new/$', 'ecs.communication.views.new_thread'),
    url(r'^submission/(?P<submission_pk>\d+)/export/$', 'ecs.core.views.export_submission'),
    url(r'^submission/(?P<submission_pk>\d+)/tasks/log/$', 'ecs.tasks.views.task_backlog'),
    url(r'^submission/(?P<submission_pk>\d+)/change_presenter/$', 'ecs.core.views.change_submission_presenter'),
    url(r'^submission/(?P<submission_pk>\d+)/change_susar_presenter/$', 'ecs.core.views.change_submission_susar_presenter'),

    url(r'^submission/(?P<submission_form_pk>\d+)/task_delete/(?P<task_pk>\d+)/$', 'ecs.core.views.submissions.delete_task'),

    url(r'^submission_form/(?P<submission_form_pk>\d+)/$', 'ecs.core.views.readonly_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/pdf/$', 'ecs.core.views.submission_pdf'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/copy/$', 'ecs.core.views.copy_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', 'ecs.core.views.copy_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/$', 'ecs.core.views.checklist_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/checklist/show/(?P<checklist_pk>\d+)/$', 'ecs.core.views.show_checklist_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/checklist/drop/(?P<checklist_pk>\d+)/$', 'ecs.core.views.drop_checklist_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/categorization/$', 'ecs.core.views.categorization_review'),
    url(r'^submission_form/(?P<submission_pk>\d+)/review/initial/$', 'ecs.core.views.initial_review'),
    url(r'^submission_form/(?P<submission_pk>\d+)/review/paper_submission/$', 'ecs.core.views.paper_submission_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/befangene/$', 'ecs.core.views.befangene_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/vote/$', 'ecs.core.views.vote_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/vote/prepare/$', 'ecs.core.views.vote_preparation'),

    url(r'^submission_form/doc/upload/(?P<docstash_key>.+)/$', 'ecs.core.views.upload_document_for_submission'),
    url(r'^submission_form/doc/delete/(?P<docstash_key>.+)/$', 'ecs.core.views.delete_document_from_submission'),
    url(r'^submission_form/new/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_submission_form'),
    url(r'^submission_form/delete/(?P<docstash_key>.+)/$', 'ecs.core.views.delete_docstash_entry'),
    url(r'^submission_form/import/$', 'ecs.core.views.import_submission_form'),
    url(r'^diff_submission_forms/(?P<old_submission_form_pk>\d+)/(?P<new_submission_form_pk>\d+)/$', 'ecs.core.views.diff'),
    url(r'^submission_widget/$', 'ecs.core.views.submission_widget'),

    url(r'^submissions/all/$', 'ecs.core.views.all_submissions'),
    url(r'^submissions/assigned/$', 'ecs.core.views.assigned_submissions'),
    url(r'^submissions/mine/$', 'ecs.core.views.my_submissions'),

    # public
    url(r'^catalog/$', 'ecs.core.views.submissions.catalog'),

    #developer
    url(r'^developer/test_pdf/$', 'ecs.core.views.developer_test_pdf'),
    url(r'^developer/test_pdf_html/(?P<submission_pk>\d+)/$', 'ecs.core.views.test_pdf_html'),
    url(r'^developer/test_render_pdf/(?P<submission_pk>\d+)/$', 'ecs.core.views.test_render_pdf'),
    url(r'^developer/test_checklist_pdf/$', 'ecs.core.views.developer_test_checklist_pdf'),
    url(r'^developer/test_checklist_pdf_html/(?P<checklist_pk>\d+)/$', 'ecs.core.views.test_checklist_pdf_html'),
    url(r'^developer/test_render_checklist_pdf/(?P<checklist_pk>\d+)/$', 'ecs.core.views.test_render_checklist_pdf'),
)

