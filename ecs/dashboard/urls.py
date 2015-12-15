# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('ecs.dashboard.views',
    url(r'^$', 'view_dashboard'),
)
