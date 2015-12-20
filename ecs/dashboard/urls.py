from django.conf.urls import url

from ecs.dashboard import views


urlpatterns = (
    url(r'^$', views.view_dashboard),
)
