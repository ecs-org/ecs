from django.conf import settings
from django.conf.urls import url

from ecs.votes import views


urlpatterns = (
    url(r'^(?P<vote_pk>\d+)/download/$', views.download_vote),
    url(r'^(?P<vote_pk>\d+)/sign$', views.vote_sign),
)

if settings.DEBUG:
    urlpatterns += (
        url(r'^(?P<vote_pk>\d+)/pdf/debug/$', views.vote_pdf_debug),
    )
