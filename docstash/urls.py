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
    url(r'^create$', 'docstash.views.create'),
)
