from django.conf.urls import url, include

from ecs.core.views.fieldhistory import field_history
from ecs.core.views.administration import advanced_settings


urlpatterns = (
    url(r'^fieldhistory/(?P<model_name>[^/]+)/(?P<pk>\d+)/$', field_history),
    url(r'^advanced_settings/$', advanced_settings),

    url(r'^submission/', include('ecs.core.urls.submission')),
    url(r'^autocomplete/', include('ecs.core.urls.autocomplete')),
    url(r'^catalog/', include('ecs.core.urls.catalog')),
)
