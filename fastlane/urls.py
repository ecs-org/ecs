# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.fastlane.views',
    url(r'^list/$', 'list'),
    url(r'^new/$', 'new'),
    url(r'^participation/(?P<meeting_pk>\d+)/$', 'participation'),
    url(r'^assistant/(?P<meeting_pk>\d+)/$', 'assistant'),
    url(r'^assistant/(?P<meeting_pk>\d+)/(?P<page_num>\d+)/$', 'assistant'),
    url(r'^assistant/start/(?P<meeting_pk>\d+)/$', 'start_assistant'),
    url(r'^assistant/stop/(?P<meeting_pk>\d+)/$', 'stop_assistant'),
)
