from django.conf.urls import url

from ecs.documents import views


urlpatterns = (
    url(r'^ref/(?P<ref_key>[0-9a-f]{32})/$', views.download_once),
)
