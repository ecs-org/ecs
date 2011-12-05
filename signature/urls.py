from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.signature.views',
    url(r'^send/$',    'sign_send'),
    url(r'^error/$',   'sign_error'),
    url(r'^preview/$', 'sign_preview'),
    url(r'^receive/$', 'sign_receive'),
    url(r'^receive/;jsessionid=null$', 'sign_receive_landing'),
)

urlpatterns += patterns('',
    url(r'^test/success/$', 'ecs.signature.tests.signaturetest.sign_success'),
    url(r'^test/failure/$', 'ecs.signature.tests.signaturetest.sign_fail'),
    )

