from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.statistics.views',
    url(r'^$', 'stats'),
    url(r'^(?P<year>\d{4})/$', 'stats'),
)