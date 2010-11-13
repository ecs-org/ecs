# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    url(r'^(?P<uuid>[0-9a-f]{32})/(?P<tiles_x>\d+)[xX](?P<tiles_y>\d+)/(?P<width>\d+)/(?P<pagenr>\d+)/$', 'ecs.mediaserver.views.docshot'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/application/pdf/brand/(?P<filename>[a-z0-9_.-]+)/$', 'ecs.mediaserver.views.download_pdf'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/application/pdf/personalize/(?P<branding>[0-9a-f]{32})/(?P<filename>[a-z0-9_.-]+)/$', 'ecs.mediaserver.views.download_pdf'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/(?P<mime_part1>[a-z]+)/(P<mime_part2>[a-z]+)/(?P<filename>[a-z0-9_.-]+)/$', 'ecs.mediaserver.views.download_blob'),
    url(r'^prepare/(?P<uuid>[0-9a-f]{32})/application/pdf/brand/$', 'ecs.mediaserver.views.prepare_with_branding'),   
    url(r'^prepare/(?P<uuid>[0-9a-f]{32})/(?P<mime_part1>[a-z]+)/(P<mime_part2>[a-z]+)/$', 'ecs.mediaserver.views.prepare'),
)

