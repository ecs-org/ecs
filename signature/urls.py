from django.conf.urls.defaults import *
import sys

urlpatterns = patterns('ecs.signature.views',
    url(r'^batch/(?P<sign_session_id>\d+)/$', 'batch_sign'),
    url(r'^send/(?P<pdf_id>\d+)/$', 'sign_send'),
    url(r'^error/(?P<pdf_id>\d+)/$', 'sign_error'),
    url(r'^preview/(?P<pdf_id>\d+)/$', 'sign_preview'),
    url(r'^action/(?P<pdf_id>\d+)/(?P<action>[^/]+)/$', 'batch_action'),

    # current version of pdf-as has some bug, to include jsessionid as part of the url
    url(r'^receive/.*$', 'sign_receive'),
)

if 'test' in sys.argv:
    urlpatterns += patterns('ecs.signature.tests.signaturetest',
        url(r'^test/success/$', 'sign_success'),
        url(r'^test/failure/$', 'sign_fail'),
    )
