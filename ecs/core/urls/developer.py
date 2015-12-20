from django.conf.urls import url

from ecs.core.views import developer as views


urlpatterns = (
    url(r'^submissions/$', views.developer_test_pdf),
    url(r'^submission/(?P<submission_pk>\d+)/html/$', views.test_pdf_html),
    url(r'^submission/(?P<submission_pk>\d+)/pdf/$', views.test_render_pdf),
    
    url(r'^checklists/$', views.developer_test_checklist_pdf),
    url(r'^checklist/(?P<checklist_pk>\d+)/html/$', views.test_checklist_pdf_html),
    url(r'^checklist/(?P<checklist_pk>\d+)/pdf/$', views.test_render_checklist_pdf),

    url(r'^notifications/$', views.developer_test_notification_pdf),
    url(r'^notification/(?P<notification_pk>\d+)/html/$', views.test_notification_pdf_html),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', views.test_render_notification_pdf),

    url(r'^notification_answers/$', views.developer_test_notification_answer_pdf),
    url(r'^notification_answer/(?P<notification_answer_pk>\d+)/html/$', views.test_notification_answer_pdf_html),
    url(r'^notification_answer/(?P<notification_answer_pk>\d+)/pdf/$', views.test_render_notification_answer_pdf),

    url(r'^votes/$', views.developer_test_vote_pdf),
    url(r'^vote/(?P<vote_pk>\d+)/html/$', views.test_vote_pdf_html),
    url(r'^vote/(?P<vote_pk>\d+)/pdf/$', views.test_render_vote_pdf),

    url(r'^translations/$', views.developer_translations),
)
