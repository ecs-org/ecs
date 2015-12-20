from django.conf.urls import url

from ecs.userswitcher import views


urlpatterns = (
    url(r'^switch/$', views.switch),
)
