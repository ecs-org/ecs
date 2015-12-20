from django.conf.urls import url

from ecs.scratchpad import views


urlpatterns = (
    url(r'^popup/(?:(?P<scratchpad_pk>\d+)/)?$', views.popup),
    url(r'^popup/list/$', views.popup_list),
)
