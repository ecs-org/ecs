from django.conf.urls import url

from ecs.tags import views


urlpatterns = (
    url(r'^$', views.index),
    url(r'^new/$', views.edit),
    url(r'^(?P<pk>\d+)/edit/$', views.edit),
    url(r'^(?P<pk>\d+)/delete/$', views.delete),
    url(r'^assign/submission/(?P<submission_pk>\d+)$', views.assign),
)
