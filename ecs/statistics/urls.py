from django.conf.urls import url

from ecs.statistics import views


urlpatterns = (
    url(r'^(?:(?P<year>\d{4})/)?$', views.stats),
)
