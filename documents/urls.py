from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.documents.views',
    url(r'^document/(?P<document_pk>\d+)/download/$', 'download_document'),
    url(r'^document/(?P<document_pk>\d+)/search/$', 'document_search'),
    url(r'^document/(?P<document_pk>\d+)/search/json/$', 'document_search_json'),
    url(r'^documents/search/$', 'document_search'),
)
