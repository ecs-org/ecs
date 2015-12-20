from django.conf.urls import url

from ecs.pki import views


urlpatterns = (
    url(r'^pki/certs/new/$', views.create_cert),
    url(r'^pki/certs/$', views.cert_list),
    url(r'^pki/certs/(?P<cert_pk>\d+)/revoke/$', views.revoke_cert),
    url(r'^secure/login/$', views.authenticate),
)
