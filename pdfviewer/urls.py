# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    url(r'^demo$', 'ecs.pdfviewer.views.demo'),
    url(r'^(?P<id>\d+)/(?P<page>\d+)/(?P<zoom>[^/]+)/$', 'ecs.pdfviewer.views.show', name='pdf_show'),
)
