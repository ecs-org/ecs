from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.signature.views',
    url(r'^signature/send$',    'sign_send'),
    url(r'^signature/error$',   'sign_error'),
    url(r'^signature/preview$', 'sign_preview'),
    url(r'^signature/receive$', 'sign_receive'),
    url(r'^signature/receive;jsessionid=null$', 'sign_receive_landing'),
    )
