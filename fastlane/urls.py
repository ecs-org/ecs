# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.fastlane.views',
    url(r'^list/$', 'list'),
    url(r'^new/$', 'new'),
    url(r'^participation/(?P<meeting_pk>\d+)/$', 'participation'),
)
