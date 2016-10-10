from django.conf.urls import url, include

from ecs.core.views import logo
from ecs.core.views.fieldhistory import field_history
from ecs.core.views.administration import advanced_settings
from ecs.core.views.autocomplete import autocomplete


urlpatterns = (
    url(r'^logo/$', logo),
    url(r'^fieldhistory/(?P<model_name>[^/]+)/(?P<pk>\d+)/$', field_history),
    url(r'^advanced_settings/$', advanced_settings),
    url(r'^autocomplete/(?P<queryset_name>[^/]+)/$', autocomplete),

    url(r'^submission/', include('ecs.core.urls.submission')),
    url(r'^comments/', include('ecs.core.urls.comments')),
    url(r'^catalog/', include('ecs.core.urls.catalog')),
)
