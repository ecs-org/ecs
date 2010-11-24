from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.boilerplate.views',
    url(r'^$', 'list_boilerplate'),
    url(r'^new/$', 'edit_boilerplate'),
    url(r'^(?P<text_pk>\d+)/edit/$', 'edit_boilerplate'),
    url(r'^(?P<text_pk>\d+)/delete/$', 'delete_boilerplate'),
    url(r'^select/$', 'select_boilerplate'),
)
