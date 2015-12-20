from django.conf.urls import url

from ecs.core.views import autocomplete as views


urlpatterns = (
    url(r'^(?P<queryset_name>[^/]+)/$', views.autocomplete),
    url(r'^internal/(?P<queryset_name>[^/]+)/$', views.internal_autocomplete),
)
