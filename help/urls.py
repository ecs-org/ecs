import os
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.help.views',
    url(r'^$', 'index'),
    url(r'^search/$', 'search'),
    
    url(r'^page/(?P<page_pk>\d+)/$', 'view_help_page'),
    url(r'^page/(?P<page_pk>\d+)/delete/$', 'delete_help_page'),
    url(r'^page/(?P<page_pk>\d+)/edit/$', 'edit_help_page'),
    url(r'^page/new/$', 'edit_help_page'),
    url(r'^page/(?P<page_pk>\d+)/ready_for_review/$', 'ready_for_review'),
    url(r'^page/(?P<page_pk>\d+)/review_ok/$', 'review_ok'),
    url(r'^page/(?P<page_pk>\d+)/review_fail/$', 'review_fail'),
    
    url(r'^view/(?P<view_pk>\d+)/', 'find_help'),
    url(r'^view/(?P<view_pk>\d+)/(?P<anchor>[\w-]+)/$', 'find_help'),
    url(r'^edit/view/(?P<view_pk>\d+)/$', 'edit_help_page'),
    url(r'^edit/view/(?P<view_pk>\d+)/(?P<anchor>[\w-]+)/$', 'edit_help_page'),

    url(r'^difference/(?P<page_pk>\d+)/$', 'difference_help_pages'),
    url(r'^difference/(?P<page_pk>\d+)/(?P<old_version>-?\d+)/(?P<new_version>-?\d+)/$', 'difference_help_pages'),

    url(r'^preview/$', 'preview_help_page_text'),
    url(r'^attachments/$', 'attachments'),
    url(r'^attachments/upload/$', 'upload'),
    url(r'^attachments/find/$', 'find_attachments'),
    url(r'^attachments/delete/$', 'delete_attachment'),
    url(r'^attachment/(?P<attachment_pk>\d+)/download/$', 'download_attachment'),
    
    url(r'^screenshot/$', 'screenshot'),

    url(r'^export/$', 'export'),
    url(r'^import/$', 'load'),
    url(r'^review/$', 'review_overview'),
)

