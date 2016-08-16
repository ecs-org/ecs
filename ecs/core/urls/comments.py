from django.conf.urls import url

from ecs.core.views import comments as views

urlpatterns = (
    url(r'^submission/(?P<submission_pk>\d+)/$', views.index),
    url(r'^submission/(?P<submission_pk>\d+)/new/$', views.edit),
    url(r'^(?P<pk>\d+)/edit/$', views.edit),
    url(r'^(?P<pk>\d+)/delete/$', views.delete),
    url(r'^(?P<pk>\d+)/attachment/$', views.download_attachment),
    url(r'^(?P<pk>\d+)/attachment/view/$', views.view_attachment),
)
