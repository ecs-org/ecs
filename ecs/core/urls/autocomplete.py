from django.conf.urls import *

urlpatterns = patterns('ecs.core.views', 
    url(r'^(?P<queryset_name>[^/]+)/$', 'autocomplete'),
    url(r'^internal/(?P<queryset_name>[^/]+)/$', 'internal_autocomplete'),
)
