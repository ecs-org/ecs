from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from core.models import Notification

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    url(r'^$', 'ecs.core.views.index'),
    url(r'^notification/new/',  'ecs.core.views.notification_new1'),
    url(r'^notification/new2/', 'ecs.core.views.notification_new2'),
    url(r'^notification/new3/', 'ecs.core.views.notification_new3'),
    url(r'^submission/(?P<submissionid>\d+)/$', 'core.views.submissiondetail'),
    url(r'^submission/\d+/notification/(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', dict(queryset=Notification.objects.all())), 
    url(r'^submission/', 'ecs.core.views.submission'),
)
