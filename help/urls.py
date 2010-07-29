# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.help.views',
    url(r'^$', 'index'),
    url(r'^page/(?P<page_pk>\d+)/$', 'view_help_page'),
    url(r'^page/new/$', 'edit_help_page'),
    url(r'^view/(?P<view_pk>\d+)/$', 'find_help'),
    url(r'^view/(?P<view_pk>\d+)/(?P<anchor>[\w-]+)/$', 'find_help'),

    url(r'^edit/page/(?P<page_pk>\d+)/$', 'edit_help_page'),
    url(r'^edit/view/(?P<view_pk>\d+)/$', 'edit_help_page'),
    url(r'^edit/view/(?P<view_pk>\d+)/(?P<anchor>[\w-]+)/$', 'edit_help_page'),
    
    url(r'^preview/$', 'preview_help_page_text'),
    url(r'^attachments/$', 'attachments'),
)
