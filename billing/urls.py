# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.billing.views',
    url(r'^submissions/$', 'submission_billing'),
    url(r'^invoice/(?P<invoice_pk>\d+)/$', 'view_invoice'),
    url(r'^invoices/$', 'invoice_list'),

    url(r'^external_review/$', 'external_review_payment'),
    url(r'^payment/(?P<payment_pk>\d+)/$', 'view_checklist_payment'),
    url(r'^payments/$', 'checklist_payment_list'),
    url(r'^external_review/reset/$', 'reset_external_review_payment'),
)
