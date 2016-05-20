from django.conf.urls import url

from ecs.votes import views


urlpatterns = (
    url(r'^(?P<vote_pk>\d+)/html/$', views.show_html_vote),
    url(r'^(?P<vote_pk>\d+)/pdf/$', views.show_pdf_vote),
    url(r'^(?P<vote_pk>\d+)/download/$', views.download_vote),
    url(r'^(?P<vote_pk>\d+)/sign$', views.vote_sign),
)
