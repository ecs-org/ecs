# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.dashboard.views',
    url(r'^$', 'view_dashboard'),
)
