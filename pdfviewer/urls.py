# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.pdfviewer.views',
    url(r'^(?P<document_pk>\d+)/$', 'show', name='pdf_show'),
    url(r'^(?P<document_pk>\d+)/annotations/share/$', 'share_annotations'),
    url(r'^(?P<document_pk>\d+)/edit-annotation/$', 'edit_annotation', name='pdf_anno'),
    url(r'^(?P<document_pk>\d+)/delete-annotation/$', 'delete_annotation', name='pdf_anno_delete'),
    url(r'^annotations/$', 'copy_annotations'),
)
