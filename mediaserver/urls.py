# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^(?P<uuid>[0-9a-f]+)/(?P<tiles_x>\d+)[xX](?P<tiles_y>\d+)/(?P<zoom>\d+)/(?P<pagenr>\d+)/$', 'ecs.mediaserver.views.docshot'),
    url(r'^upload/$', 'ecs.mediaserver.views.upload_pdf'),
    url(r'^download/$', 'ecs.mediaserver.views.download_pdf'),
)
