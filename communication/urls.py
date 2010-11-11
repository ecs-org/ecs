# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.communication.views',
    url(r'^threads/$', 'threads'),
    url(r'^send/(?:(?P<submission_pk>\d+)/)?$', 'send_message'),
    url(r'^send/(?P<submission_pk>\d+)/to/(?P<to_user_pk>\d+)/$', 'send_message'),
    url(r'^message/(?P<thread_pk>\d+)/read/$', 'read_thread'),
    url(r'^message/(?P<reply_to_pk>\d+)/reply/$', 'send_message'),
    url(r'^message/(?P<message_pk>\d+)/bump/$', 'bump_message'),
    url(r'^thread/(?P<thread_pk>\d+)/close/$', 'close_thread'),
    url(r'^thread/(?P<thread_pk>\d+)/delegate/$', 'delegate_thread'),
    url(r'^widgets/incoming_messages/$', 'incoming_message_widget'),
    url(r'^widgets/outgoing_messages/$', 'outgoing_message_widget'),
    url(r'^widgets/communication_overview/(?P<submission_pk>\d+)$', 'communication_overview_widget'),
)
