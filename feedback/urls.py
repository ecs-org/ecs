#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-
#
# (c) 2009 Medizinische Universität Wien
#
"""
URL map for feedback backend.
"""

from django.conf.urls.defaults import *
from piston.resource import Resource

from feedback.handlers import FeedbackHandler, FeedbackCreate, FeedbackSearch

feedbackpost_resource = Resource(handler=FeedbackHandler)
feedbackpost_create = Resource(handler=FeedbackCreate)
feedbackpost_search = Resource(handler=FeedbackSearch)


def test(*args, **kw):
    print "args", args
    print "kw", kw
    return None

urlpatterns = patterns(
    '',
    url(r'^$', feedbackpost_create),
    
    url(r'^input/$', 'ecs.feedback.views.feedback_input'),
    url(r'^input/(?P<type>[a-z])/$', 'ecs.feedback.views.feedback_input'),
    url(r'^input/(?P<type>[a-z])/(?P<page>\d+)/$', 'ecs.feedback.views.feedback_input'),
    url(r'^input/(?P<type>[a-z])/(?P<page>\d+)/(?P<origin>[^/]+)/$', 'ecs.feedback.views.feedback_input', name='feedback_input'),
    
    url(r'^(?P<pk>[^/]+)$', feedbackpost_resource), 
    url(r'^(?P<type>[^/]+)/(?P<origin>[^/]+)/(?P<offsetdesc>.*)$', feedbackpost_search), 
    #url(r'^(?P<pk>.*)$', test),
)

#
# monkey patching django piston so it can handle charsets in the content-type header.
# (it's here because urls.py is imported for sure before the first request being processed.
#

from piston import utils

def content_type(self):
    """
    Returns the content type of the request in all cases where it is
    different than a submitted form - application/x-www-form-urlencoded
    """
    type_formencoded = "application/x-www-form-urlencoded"
    
    ctype = self.request.META.get('CONTENT_TYPE', type_formencoded).split(";")[0]
    
    if ctype == type_formencoded:
        return None
    
    return ctype

utils.Mimer.content_type = content_type
