#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^$', 'ecs.pdfviewer.views.show'),
    url(r'^(?P<id>\d+)/(?P<page>\d+)/(?P<zoom>[^/]+)/$', 'ecs.pdfviewer.views.show', name='pdf_show'),
    url(r'^demo/$', 'ecs.pdfviewer.views.demo'),
)
