from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.groupchooser.views',
    url(r'^choose/$', 'choose'),
)
