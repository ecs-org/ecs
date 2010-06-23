# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    url(r'^demo$', 'ecs.pdfsigner.views.demo'),
    url(r'^sign$', 'ecs.pdfsigner.views.demo_sign'),
    url(r'^send$', 'ecs.pdfsigner.views.demo_send'),
    url(r'^error$', 'ecs.pdfsigner.views.demo_error'),
    url(r'^receive$', 'ecs.pdfsigner.views.demo_receive'),
    url(r'^receive;jsessionid=(?P<jsessionid>[^?]*)$', 'ecs.pdfsigner.views.demo_receive'),
)
