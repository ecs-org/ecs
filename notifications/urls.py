# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.notifications.views',
    url(r'^notification/new/$', 'select_notification_creation_type'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/diff/(?P<submission_form_pk>\d+)/$', 'create_diff_notification'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', 'create_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/$', 'view_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'notification_pdf'),
    url(r'^notifications/$', 'notification_list'),
    url(r'^submission_data_for_notification/$', 'submission_data_for_notification'),
)