from django.conf.urls import url

from ecs.docstash import views


urlpatterns = (
    url(r'^(?P<docstash_key>.+)/doc/(?P<document_pk>\d+)/$', views.download_document),
    url(r'^(?P<docstash_key>.+)/doc/(?P<document_pk>\d+)/view/$', views.view_document),
)
