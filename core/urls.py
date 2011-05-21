from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/dashboard/', 'permanent': True}),
    url(r'^autocomplete/(?P<queryset_name>[^/]+)/$', 'ecs.core.views.autocomplete'),

    url(r'^submission/(?P<submission_pk>\d+)/$', 'ecs.core.views.view_submission'),
    url(r'^submission/(?P<submission_pk>\d+)/copy_form/$', 'ecs.core.views.copy_latest_submission_form'),
    url(r'^submission/(?P<submission_pk>\d+)/messages/new/$', 'ecs.communication.views.new_thread'),
    url(r'^submission/(?P<submission_pk>\d+)/export/$', 'ecs.core.views.export_submission'),
    url(r'^submission/(?P<submission_pk>\d+)/tasks/log/$', 'ecs.tasks.views.task_backlog'),

    url(r'^submission/(?P<submission_form_pk>\d+)/task_delete/(?P<task_pk>\d+)/$', 'ecs.core.views.submissions.delete_task'),

    url(r'^submission_form/(?P<submission_form_pk>\d+)/$', 'ecs.core.views.readonly_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/pdf/$', 'ecs.core.views.submission_pdf'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/copy/$', 'ecs.core.views.copy_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/amend/(?P<notification_type_pk>\d+)/$', 'ecs.core.views.copy_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/$', 'ecs.core.views.checklist_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/categorization/$', 'ecs.core.views.categorization_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/befangene/$', 'ecs.core.views.befangene_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/vote/$', 'ecs.core.views.vote_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/b2vote/$', 'ecs.core.views.b2_vote_review'),

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
    
    url(r'^vote/(?P<vote_pk>\d+)/show/html$', 'ecs.core.views.show_html_vote'),
    url(r'^vote/(?P<vote_pk>\d+)/show/pdf$', 'ecs.core.views.show_pdf_vote'),
    url(r'^vote/(?P<vote_pk>\d+)/download$', 'ecs.core.views.download_signed_vote'),   
    url(r'^vote/(?P<vote_pk>\d+)/sign$', 'ecs.core.views.vote_sign'),
    url(r'^vote/(?P<document_pk>\d+)/sign_finished/$', 'ecs.core.views.vote_sign_finished'),
    
    url(r'^checklist/(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', 'ecs.core.views.checklist_comments'),

    url(r'^wizard/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.wizard'),

    # public
    url(r'^catalog/$', 'ecs.core.views.submissions.catalog'),

    #developer
    url(r'^developer/test_pdf/$', 'ecs.core.views.developer_test_pdf'),
    url(r'^developer/test_pdf_html/(?P<submission_pk>\d+)/$', 'ecs.core.views.test_pdf_html'),
    url(r'^developer/test_render_pdf/(?P<submission_pk>\d+)/$', 'ecs.core.views.test_render_pdf'),
)

