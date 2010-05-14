# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.messages.views',
    url(r'^inbox/$', 'inbox'),
    url(r'^outbox/$', 'outbox'),
    url(r'^list/$', 'list_messages'),
    url(r'^send/(?:(?P<submission_pk>\d+)/)?$', 'send_message'),
    url(r'^message/(?P<message_pk>\d+)/read/$', 'read_message'),
    url(r'^message/(?P<reply_to_pk>\d+)/reply/$', 'send_message'),
)
