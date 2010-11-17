# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.fastlane.views',
    url(r'^list/$', 'list'),
    url(r'^new/$', 'new'),
    url(r'^status/(?P<meeting_pk>\d+)/$', 'status'),
    url(r'^participation/(?P<meeting_pk>\d+)/$', 'participation'),
    url(r'^invitations/(?P<meeting_pk>\d+)/$', 'invitations'),
    url(r'^invitations/(?P<meeting_pk>\d+)/(?P<reallysure>reallysure)/$', 'invitations'),
    url(r'^assistant/(?P<meeting_pk>\d+)/$', 'assistant'),
    url(r'^assistant/(?P<meeting_pk>\d+)/(?P<page_num>\d+)/$', 'assistant'),
    url(r'^assistant/start/(?P<meeting_pk>\d+)/$', 'start_assistant'),
    url(r'^assistant/stop/(?P<meeting_pk>\d+)/$', 'stop_assistant'),
    url(r'^copy_comment/(?P<top_pk>\d+)/$', 'copy_comment'),
)
