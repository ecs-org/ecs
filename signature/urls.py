from django.conf.urls.defaults import *
import sys

urlpatterns = patterns('ecs.signature.views',
    url(r'^send/$',    'sign_send'),
    url(r'^error/(?P<pdf_id>\d+)/$',   'sign_error'),
    url(r'^preview/$', 'sign_preview'),

    # current version of pdf-as has some bug, to include jsessionid as part of the url
    url(r'^receive/.*$', 'sign_receive'),
)

if 'test' in sys.argv:
    urlpatterns += patterns('ecs.signature.tests.signaturetest',
        url(r'^test/success/$', 'sign_success'),
        url(r'^test/failure/$', 'sign_fail'),
    )
