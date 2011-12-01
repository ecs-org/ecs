from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.documents.views',
    url(r'^(?P<document_pk>\d+)/download/$', 'download_document'),
    url(r'^(?P<document_pk>\d+)/search/json/$', 'document_search_json'),
)
