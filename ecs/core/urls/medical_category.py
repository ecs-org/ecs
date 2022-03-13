from django.conf.urls import url

from ecs.core.views import medical_category as views

urlpatterns = (
    url(r'^', views.index),
)
