from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.votes.views',
    url(r'^(?P<vote_pk>\d+)/html/$', 'show_html_vote'),
    url(r'^(?P<vote_pk>\d+)/pdf/$', 'show_pdf_vote'),
    url(r'^(?P<vote_pk>\d+)/download/$', 'download_signed_vote'),
    url(r'^(?P<vote_pk>\d+)/sign$', 'vote_sign'),
)
