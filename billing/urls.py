# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.billing.views',
    url(r'^submissions/$', 'submission_billing'),
    url(r'^external_review/$', 'external_review_payment'),
)

if settings.DEBUG:
    # development-only views
    urlpatterns += patterns('ecs.billing.views',
        url(r'^submissions/reset/$', 'reset_submissions'),
        url(r'^external_review/reset/$', 'reset_external_review_payment'),
    )
