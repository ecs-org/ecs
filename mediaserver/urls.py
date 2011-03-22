# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    url(r'^(?P<uuid>[0-9a-f]{32})/(?P<tiles_x>\d+)[xX](?P<tiles_y>\d+)/(?P<width>\d+)/(?P<pagenr>\d+)/$', 'ecs.mediaserver.views.get_page'),
    url(r'^prime/(?P<uuid>[0-9a-f]{32})/$', 'ecs.mediaserver.views.prime_cache'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/application/pdf/brand/(?P<filename>[a-z0-9_.-]+)/$', 'ecs.mediaserver.views.get_pdf'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/application/pdf/personalize/(?P<branding>[0-9a-f]{32})/(?P<filename>[a-z0-9_.-]+)/$', 'ecs.mediaserver.views.get_pdf'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/(?P<mimetype>[a-z]+/[a-z.-]+)/(?P<filename>[a-zA-Z0-9_.-]+)/$', 'ecs.mediaserver.views.get_blob'),
    url(r'^prepare/(?P<uuid>[0-9a-f]{32})/application/pdf/brand/$', 'ecs.mediaserver.views.prepare_branded'),   
    url(r'^prepare/(?P<uuid>[0-9a-f]{32})/(?P<mimetype>[a-z]+/[a-z.-]+)/$', 'ecs.mediaserver.views.prepare'),
)

