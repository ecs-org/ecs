from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.audit.views',
    url(r'^log/(?P<format>\w+)/$', 'log'),
    url(r'^log/(?P<format>\w+)/limit=(?P<limit>\d+)/until=(?P<until>[^/]+)/$', 'log'),
    url(r'^log/(?P<format>\w+)/limit=(?P<limit>\d+)/since=(?P<since>[^/]+)/$', 'log'),
)
