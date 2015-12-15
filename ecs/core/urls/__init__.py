from django.conf.urls.defaults import *
from django.views.generic.base import RedirectView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/dashboard/', permanent=True)),
    url(r'^fieldhistory/(?P<model_name>[^/]+)/(?P<pk>\d+)/$', 'ecs.core.views.field_history'),
    url(r'^advanced_settings/$', 'ecs.core.views.advanced_settings'),

    url(r'^submission/', include('ecs.core.urls.submission')),
    url(r'^autocomplete/', include('ecs.core.urls.autocomplete')),
    url(r'^catalog/', include('ecs.core.urls.catalog')),
    url(r'^developer/', include('ecs.core.urls.developer')),
)
