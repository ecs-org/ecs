from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.scratchpad.views',
    url(r'^popup/$', 'popup'),
    url(r'^popup/(?P<scratchpad_pk>\d+)/$', 'popup'),
    url(r'^popup/list/$', 'popup_list'),
)
