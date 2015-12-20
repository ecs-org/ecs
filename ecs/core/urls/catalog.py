from django.conf.urls import url

from ecs.core.views import submissions as views


urlpatterns = (
    url(r'^(?:(?P<year>\d+)/)?$', views.catalog),
    url(r'^json/$', views.catalog_json),
)
