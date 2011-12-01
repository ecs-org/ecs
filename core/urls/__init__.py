from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/dashboard/', 'permanent': True}),
    url(r'^fieldhistory/(?P<model_name>[^/]+)/(?P<pk>\d+)/$', 'ecs.core.views.field_history'),

    url(r'^submission/', include('ecs.core.urls.submission')),
    url(r'^autocomplete/', include('ecs.core.urls.autocomplete')),
    url(r'^catalog/', include('ecs.core.urls.catalog')),
    url(r'^developer/', include('ecs.core.urls.developer')),
)
