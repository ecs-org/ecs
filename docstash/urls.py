# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#
"""
Urlmap for docstash
"""

from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^create/(?P<form>.*)/$', 'docstash.views.create'),
    url(r'^(?P<key>[0-9A-Fa-f]+)$', 'docstash.views.read'),
    url(r'^(?P<key>[0-9A-Fa-f]+)/(?P<version>[\d-]+)$', 'docstash.views.post'),
)
