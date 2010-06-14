# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    url(r'^demo$', 'ecs.pdfsigner.views.demo'),
    url(r'^sign_pdf$', 'ecs.pdfsigner.views.sign_pdf'),
    url(r'^send_pdf$', 'ecs.pdfsigner.views.send_pdf'),
    url(r'^sign_pdf_error$', 'ecs.pdfsigner.views.sign_pdf_error'),
    url(r'^receive_pdf$', 'ecs.pdfsigner.views.receive_pdf'),
    url(r'^receive_pdf;jsessionid=(?P<jsessionid>[^?]*)$', 'ecs.pdfsigner.views.receive_pdf'),
)
