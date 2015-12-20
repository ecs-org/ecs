import sys

from django.conf.urls import url

from ecs.signature import views


urlpatterns = (
    url(r'^batch/(?P<sign_session_id>\d+)/$', views.batch_sign),
    url(r'^send/(?P<pdf_id>\d+)/$', views.sign_send),
    url(r'^error/(?P<pdf_id>\d+)/$', views.sign_error),
    url(r'^preview/(?P<pdf_id>\d+)/$', views.sign_preview),
    url(r'^action/(?P<pdf_id>\d+)/(?P<action>[^/]+)/$', views.batch_action),
    url(r'^receive/(?P<pdf_id>\d+)/$', views.sign_receive),
)

if 'test' in sys.argv:
    from ecs.signature.tests import sign_success, sign_fail
    urlpatterns += (
        url(r'^test/success/$', sign_success),
        url(r'^test/failure/$', sign_fail),
    )
