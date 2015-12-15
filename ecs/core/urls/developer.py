from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.core.views', 
    url(r'^submissions/$', 'developer_test_pdf'),
    url(r'^submission/(?P<submission_pk>\d+)/html/$', 'test_pdf_html'),
    url(r'^submission/(?P<submission_pk>\d+)/pdf/$', 'test_render_pdf'),
    
    url(r'^checklists/$', 'developer_test_checklist_pdf'),
    url(r'^checklist/(?P<checklist_pk>\d+)/html/$', 'test_checklist_pdf_html'),
    url(r'^checklist/(?P<checklist_pk>\d+)/pdf/$', 'test_render_checklist_pdf'),

    url(r'^notifications/$', 'developer_test_notification_pdf'),
    url(r'^notification/(?P<notification_pk>\d+)/html/$', 'test_notification_pdf_html'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'test_render_notification_pdf'),

    url(r'^notification_answers/$', 'developer_test_notification_answer_pdf'),
    url(r'^notification_answer/(?P<notification_answer_pk>\d+)/html/$', 'test_notification_answer_pdf_html'),
    url(r'^notification_answer/(?P<notification_answer_pk>\d+)/pdf/$', 'test_render_notification_answer_pdf'),

    url(r'^votes/$', 'developer_test_vote_pdf'),
    url(r'^vote/(?P<vote_pk>\d+)/html/$', 'test_vote_pdf_html'),
    url(r'^vote/(?P<vote_pk>\d+)/pdf/$', 'test_render_vote_pdf'),

    url(r'^translations/$', 'developer_translations'),
)
