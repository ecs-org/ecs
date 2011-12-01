# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.billing.views',
    url(r'^submissions/$', 'submission_billing'),
    url(r'^submissions/reset/$', 'reset_submissions'),
    url(r'^external_review/$', 'external_review_payment'),
    url(r'^external_review/reset/$', 'reset_external_review_payment'),
)
