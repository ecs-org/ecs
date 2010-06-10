# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    url(r'^signpdf$', 'ecs.mediaserver.views.sign_pdf'),
    url(r'^sendpdf$', 'ecs.mediaserver.views.send_pdf'),
    url(r'^signpdferror$', 'ecs.mediaserver.views.sign_pdf_error'),
    url(r'^receivepdf$', 'ecs.mediaserver.views.receive_pdf'),
    url(r'^receivepdf;jsessionid=(?P<jsessionid>[^?]*)$', 'ecs.mediaserver.views.receive_pdf'),
    url(r'^(?P<id>\d+)/(?P<bigpage>\d+)/(?P<zoom>[^/]+)/$', 'ecs.mediaserver.views.get_image'),
)
