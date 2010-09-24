from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
    '',
    url(r'^log/(?P<format>\w+)/$', 'ecs.audit.views.log'),
)
