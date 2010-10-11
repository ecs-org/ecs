#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2009 Medizinische Universität Wien
#
"""
URL map for feedback backend.
"""

from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^input/$', 'ecs.feedback.views.feedback_input'),
    url(r'^input/(?P<type>[a-z])/$', 'ecs.feedback.views.feedback_input'),
    url(r'^input/(?P<type>[a-z])/(?P<page>\d+)/$', 'ecs.feedback.views.feedback_input'),
    url(r'^input/(?P<type>[a-z])/(?P<page>\d+)/(?P<origin>[^/]+)/$', 'ecs.feedback.views.feedback_input', name='feedback_input'),
    
)

