# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.dashboard.views',
    url(r'^$', 'view_dashboard'),
    url(r'^message/(?P<message_pk>\d+)/read/$', 'read_message'),
)
