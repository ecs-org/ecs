# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.notifications.views',
    url(r'^new/$', 'select_notification_creation_type'),
    url(r'^new/(?P<notification_type_pk>\d+)/diff/(?P<submission_form_pk>\d+)/$', 'create_diff_notification'),
    url(r'^new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', 'create_notification'),
    url(r'^delete/(?P<docstash_key>.+)/$', 'delete_docstash_entry'),
    url(r'^doc/upload/(?P<docstash_key>.+)/$', 'upload_document_for_notification'),
    url(r'^doc/delete/(?P<docstash_key>.+)/$', 'delete_document_from_notification'),
    url(r'^submission_data_for_notification/$', 'submission_data_for_notification'),

    url(r'^(?P<notification_pk>\d+)/$', 'view_notification'),
    url(r'^(?P<notification_pk>\d+)/pdf/$', 'notification_pdf'),
    url(r'^(?P<notification_pk>\d+)/answer/$', 'view_notification_answer'),
    url(r'^(?P<notification_pk>\d+)/answer/edit/$', 'edit_notification_answer'),
    url(r'^(?P<notification_pk>\d+)/answer/pdf/$', 'notification_answer_pdf'),

    url(r'^list/open/$', 'open_notifications'),
    url(r'^list/answered/$', 'answered_notifications'),
)
