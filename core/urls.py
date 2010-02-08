from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    url(r'^$', 'ecs.core.views.index'),
    url(r'^submission/', 'ecs.core.views.submission'),
    url(r'^notification/new/',  'ecs.core.views.notification_new1'),
    url(r'^notification/new2/', 'ecs.core.views.notification_new2'),
    url(r'^notification/new3/', 'ecs.core.views.notification_new3'),
    url(r'^notification/new4/', 'ecs.core.views.notification_new4'),
)
