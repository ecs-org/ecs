# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.communication.views',
    url(r'^list/$', 'list_threads'),
    url(r'^widget/incoming/$', 'incoming_message_widget'),
    url(r'^widget/outgoing/$', 'outgoing_message_widget'),
    url(r'^widget/overview/(?P<submission_pk>\d+)$', 'communication_overview_widget'),

    url(r'^new/(?:(?P<submission_pk>\d+)/)?$', 'new_thread'),
    url(r'^new/(?P<submission_pk>\d+)/to/(?P<to_user_pk>\d+)/$', 'new_thread'),

    url(r'^(?P<thread_pk>\d+)/read/$', 'read_thread'),
    url(r'^(?P<thread_pk>\d+)/close/$', 'close_thread'),
)
