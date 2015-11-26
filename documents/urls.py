from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.documents.views',
    url(r'^(?P<document_pk>\d+)/view/(?:page/(?P<page>\d+)/)?$', 'view_document'),
    url(r'^ref/(?P<ref_key>[0-9a-f]{32})/$', 'download_once'),
    url(r'^(?P<document_pk>\d+)/download/$', 'download_document'),
)
