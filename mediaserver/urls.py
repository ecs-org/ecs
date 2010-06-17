# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    url(r'^(?P<id>[0-9a-f]+)/(?P<bigpage>\d+)/(?P<zoom>[^/]+)/$', 'ecs.mediaserver.views.get_image'),
)
