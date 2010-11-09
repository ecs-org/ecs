# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<document_pk>\d+)/$', 'ecs.pdfviewer.views.show', name='pdf_show'),
    url(r'^(?P<document_pk>\d+)/annotations/share/$', 'ecs.pdfviewer.views.share_annotations'),
    url(r'^(?P<document_pk>\d+)/edit-annotation/$', 'ecs.pdfviewer.views.edit_annotation', name='pdf_anno'),
    url(r'^(?P<document_pk>\d+)/delete-annotation/$', 'ecs.pdfviewer.views.delete_annotation', name='pdf_anno_delete'),
    url(r'^annotations/$', 'ecs.pdfviewer.views.copy_annotations'),
)
