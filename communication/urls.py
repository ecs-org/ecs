# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.communication.views',
    url(r'^list/$', 'list_threads'),
    url(r'^new/(?:(?P<submission_pk>\d+)/)?$', 'new_thread'),
    url(r'^new/(?P<submission_pk>\d+)/to/(?P<to_user_pk>\d+)/$', 'new_thread'),
    url(r'^read/(?P<thread_pk>\d+)/$', 'read_thread'),
    url(r'^close/(?P<thread_pk>\d+)/$', 'close_thread'),
    url(r'^widgets/incoming_messages/$', 'incoming_message_widget'),
    url(r'^widgets/outgoing_messages/$', 'outgoing_message_widget'),
    url(r'^widgets/communication_overview/(?P<submission_pk>\d+)$', 'communication_overview_widget'),
)
