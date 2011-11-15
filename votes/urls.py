from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.votes.views',
    url(r'^show/(?P<vote_pk>\d+)/html/$', 'show_html_vote'),
    url(r'^show/(?P<vote_pk>\d+)/pdf/$', 'show_pdf_vote'),
    url(r'^download/(?P<vote_pk>\d+)/$', 'download_signed_vote'),
    url(r'^sign/(?P<vote_pk>\d+)/$', 'vote_sign'),
    url(r'^sign/(?P<document_pk>\d+)/finished/$', 'vote_sign_finished'),
)
