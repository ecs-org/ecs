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
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', dict(document_root=settings.MEDIA_ROOT)),
    url(r'^submission/', 'ecs.core.views.submission'),
    url(r'^notification/', 'ecs.core.views.notification'),
)
