# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^(?P<uuid>[0-9a-f-]+)/(?P<tiles_x>\d+)[xX](?P<tiles_y>\d+)/(?P<width>\d+)/(?P<pagenr>\d+)/$', 'ecs.mediaserver.views.docshot'),
    url(r'^download/(?P<uuid>[0-9a-f-]+)/$', 'ecs.mediaserver.views.download_pdf'),
    
    url(r'^upload/$', 'ecs.mediaserver.views.upload_pdf'), # FIXME: TEST Function, not production
)
