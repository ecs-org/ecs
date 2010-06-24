# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.messages.views',
    url(r'^inbox/$', 'inbox'),
    url(r'^outbox/$', 'outbox'),
    url(r'^send/(?:(?P<submission_pk>\d+)/)?$', 'send_message'),
    url(r'^message/(?P<thread_pk>\d+)/read/$', 'read_thread'),
    url(r'^message/(?P<reply_to_pk>\d+)/reply/$', 'send_message'),
    url(r'^message/(?P<message_pk>\d+)/bump/$', 'bump_message'),
    url(r'^thread/(?P<thread_pk>\d+)/close/$', 'close_thread'),
    url(r'^thread/(?P<thread_pk>\d+)/delegate/$', 'delegate_thread'),
    url(r'^widgets/incoming_messages/$', 'incoming_message_widget'),
    url(r'^widgets/outgoing_messages/$', 'outgoing_message_widget'),
)
