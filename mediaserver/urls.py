from django.conf.urls.defaults import *

urlpatterns = patterns('ecs.mediaserver.views',
    url(r'^download/(?P<uuid>[0-9a-f]{32})/application/pdf/brand/(?P<branding>True)/(?P<filename>[a-z0-9_.-]+)/$', 'get_pdf'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/application/pdf/brand/(?P<branding>[0-9a-f]{32})/(?P<filename>[a-z0-9_.-]+)/$', 'get_pdf'),
    url(r'^download/(?P<uuid>[0-9a-f]{32})/(?P<mimetype>[a-z]+/[a-z.-]+)/(?P<filename>[a-zA-Z0-9_.-]+)/$', 'get_blob'),
)

