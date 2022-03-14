from django.conf.urls import url

from ecs.core.views import medical_category as views

urlpatterns = (
    url(r'^$', views.administration),
    url(r'^new', views.create_medical_category),
    url(r'^(?P<pk>\d+)$', views.update_medical_category),
    url(r'^toggle/(?P<pk>\d+)$', views.toggle_disabled),
)
