from django.conf.urls import url

from ecs.boilerplate import views


urlpatterns = (
    url(r'^list/$', views.list_boilerplate),
    url(r'^new/$', views.edit_boilerplate),
    url(r'^(?P<text_pk>\d+)/edit/$', views.edit_boilerplate),
    url(r'^(?P<text_pk>\d+)/delete/$', views.delete_boilerplate),
    url(r'^select/$', views.select_boilerplate),
)
