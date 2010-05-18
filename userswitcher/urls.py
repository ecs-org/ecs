from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.userswitcher.views',
    url(r'^switch/$', 'switch'),
)
