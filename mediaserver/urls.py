# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    url(r'^(?P<uuid>[0-9a-f]{32})/(?P<tiles_x>\d+)[xX](?P<tiles_y>\d+)/(?P<width>\d+)/(?P<pagenr>\d+)/$', 'ecs.mediaserver.views.docshot'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/$', 'ecs.mediaserver.views.download_pdf'),
)

