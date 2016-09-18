from django.conf import settings
from django.conf.urls import url

from ecs.notifications import views


urlpatterns = (
    url(r'^new/$', views.select_notification_creation_type),
    url(r'^new/(?P<notification_type_pk>\d+)/diff/(?P<submission_form_pk>\d+)/$', views.create_diff_notification),
    url(r'^new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', views.create_notification),
    url(r'^delete/(?P<docstash_key>.+)/$', views.delete_docstash_entry),
    url(r'^doc/upload/(?P<docstash_key>.+)/$', views.upload_document_for_notification),
    url(r'^doc/delete/(?P<docstash_key>.+)/$', views.delete_document_from_notification),
    url(r'^submission_data_for_notification/$', views.submission_data_for_notification),
    url(r'^investigators_for_notification/$', views.investigators_for_notification),
    url(r'^(?P<notification_pk>\d+)/$', views.view_notification),
    url(r'^(?P<notification_pk>\d+)/pdf/$', views.notification_pdf),
    url(r'^(?P<notification_pk>\d+)/doc/(?P<document_pk>\d+)/$', views.download_document),
    url(r'^(?P<notification_pk>\d+)/doc/(?P<document_pk>\d+)/view/$', views.view_document),
    url(r'^(?P<notification_pk>\d+)/answer/$', views.view_notification_answer),
    url(r'^(?P<notification_pk>\d+)/answer/pdf/$', views.notification_answer_pdf),
    url(r'^(?P<notification_pk>\d+)/answer/edit/$', views.edit_notification_answer),
    url(r'^(?P<notification_pk>\d+)/answer/sign/$', views.notification_answer_sign),
    url(r'^list/open/$', views.open_notifications),
)

if settings.DEBUG:
    urlpatterns += (
        url(r'^(?P<notification_pk>\d+)/pdf/debug/$', views.notification_pdf_debug),
        url(r'^(?P<notification_pk>\d+)/answer/pdf/debug/$', views.notification_answer_pdf_debug),
    )
