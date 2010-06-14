# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    url(r'^demo$', 'ecs.pdfsigner.views.demo'),
    url(r'^demo_sign_pdf$', 'ecs.pdfsigner.views.demo_sign_pdf'),
    url(r'^demo_send_pdf$', 'ecs.pdfsigner.views.demo_send_pdf'),
    url(r'^demo_sign_pdf_error$', 'ecs.pdfsigner.views.demo_sign_pdf_error'),
    url(r'^demo_receive_pdf$', 'ecs.pdfsigner.views.demo_receive_pdf'),
    url(r'^demo_receive_pdf;jsessionid=(?P<jsessionid>[^?]*)$', 'ecs.pdfsigner.views.demo_receive_pdf'),
)
