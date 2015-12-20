from django.conf.urls import url

from ecs.documents import views


urlpatterns = (
    url(r'^(?P<document_pk>\d+)/view/(?:page/(?P<page>\d+)/)?$', views.view_document),
    url(r'^ref/(?P<ref_key>[0-9a-f]{32})/$', views.download_once),
    url(r'^(?P<document_pk>\d+)/download/$', views.download_document),
)
