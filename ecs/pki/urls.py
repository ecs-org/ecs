from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.pki.views',
    url(r'^pki/certs/new/$', 'create_cert'),
    url(r'^pki/certs/$', 'cert_list'),
    url(r'^pki/certs/(?P<cert_pk>\d+)/revoke/$', 'revoke_cert'),
    url(r'^secure/login/$', 'authenticate'),
)

