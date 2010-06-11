# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.dashboard.views',
    url(r'^$', 'view_dashboard'),
    url(r'^message/(?P<message_pk>\d+)/read/$', 'read_message'),
    url(r'^widgets/incoming_messages/$', 'incoming_message_widget'),
    url(r'^widgets/outgoing_messages/$', 'outgoing_message_widget'),
)
