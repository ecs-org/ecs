# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.fastlane.views',
    url(r'^create_meeting/$', 'create_fast_lane_meeting'),
)
