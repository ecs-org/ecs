from django.conf.urls import *

urlpatterns = patterns('ecs.core.views', 
    url(r'^(?:(?P<year>\d+)/)?$', 'submissions.catalog'),
    url(r'^json/$', 'submissions.catalog_json'),
)
