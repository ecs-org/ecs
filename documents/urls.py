from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.documents.views',
    url(r'^document/(?P<document_pk>\d+)/download/$', 'download_document'),
    url(r'^document/(?P<document_pk>\d+)/search/$', 'document_search'),
    url(r'^documents/search/$', 'document_search'),
)
