from django.conf.urls.defaults import *
import sys

urlpatterns = patterns('ecs.signature.views',
    url(r'^send/$',    'sign_send'),
    url(r'^error/$',   'sign_error'),
    url(r'^preview/$', 'sign_preview'),

    # current version of pdf-as has some bug, to include jsessionid as part of the url
    url(r'^receive/(;jsessionid=null)?$', 'sign_receive'),
)

if 'test' in sys.argv:
    urlpatterns += patterns('',
        url(r'^test/success/$', 'ecs.signature.tests.signaturetest.sign_success'),
        url(r'^test/failure/$', 'ecs.signature.tests.signaturetest.sign_fail'),
    )
