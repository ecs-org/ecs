from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url(r'^log/(?P<format>\w+)/$', 'ecs.audit.views.log'),
    url(r'^log/(?P<format>\w+)/limit=(?P<limit>\d+)/until=(?P<until>[^/]+)/$', 'ecs.audit.views.log'),
    url(r'^log/(?P<format>\w+)/limit=(?P<limit>\d+)/since=(?P<since>[^/]+)/$', 'ecs.audit.views.log'),
)
