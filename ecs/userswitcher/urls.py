from django.conf.urls import *

urlpatterns = patterns('ecs.userswitcher.views',
    url(r'^switch/$', 'switch'),
)
