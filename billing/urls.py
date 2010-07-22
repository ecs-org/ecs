# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.billing.views',
    url(r'^submissions/$', 'submission_billing'),
)
