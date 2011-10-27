# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.notifications.views',
    url(r'^notification/new/$', 'select_notification_creation_type'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/diff/(?P<submission_form_pk>\d+)/$', 'create_diff_notification'),
    url(r'^notification/doc/upload/(?P<docstash_key>.+)/$', 'upload_document_for_notification'),
    url(r'^notification/doc/delete/(?P<docstash_key>.+)/$', 'delete_document_from_notification'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', 'create_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/$', 'view_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'notification_pdf'),
    url(r'^notification/(?P<notification_pk>\d+)/answer/$', 'view_notification_answer'),
    url(r'^notification/(?P<notification_pk>\d+)/answer/edit/$', 'edit_notification_answer'),
    url(r'^notification/(?P<notification_pk>\d+)/answer/pdf/$', 'notification_answer_pdf'),
    url(r'^notifications/open/$', 'open_notifications'),
    url(r'^notifications/answered/$', 'answered_notifications'),
    url(r'^notifications/delete/(?P<docstash_key>.+)/$', 'delete_docstash_entry'),
    url(r'^submission_data_for_notification/$', 'submission_data_for_notification'),
)
