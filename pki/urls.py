from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.pki.views',
    url(r'^certs/new/$', 'create_cert'),
    url(r'^certs/$', 'cert_list'),
    url(r'^certs/(?P<cert_pk>\d+)/revoke/$', 'revoke_cert'),
)

