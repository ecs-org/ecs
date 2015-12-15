from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.core.views', 
    url(r'^(?P<queryset_name>[^/]+)/$', 'autocomplete'),
    url(r'^internal/(?P<queryset_name>[^/]+)/$', 'internal_autocomplete'),
)
