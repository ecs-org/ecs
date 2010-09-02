from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from django.views.generic.simple import direct_to_template
from ecs.utils import forceauth
import django

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/dashboard/'}),

    url(r'^core/', include('core.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^docstash/', include('docstash.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^feedback/', include('ecs.feedback.urls')),
    url(r'^userswitcher/', include('ecs.userswitcher.urls')),
    url(r'^pdfsigner/', include('ecs.pdfsigner.urls')),
    url(r'^pdfviewer/', include('ecs.pdfviewer.urls')),
    url(r'^mediaserver/', include('ecs.mediaserver.urls')),
    url(r'^tasks/', include('ecs.tasks.urls')),
    url(r'^messages/', include('ecs.messages.urls')),
    url(r'^billing/', include('ecs.billing.urls')),
    url(r'^help/', include('ecs.help.urls')),
    url(r'^', include('ecs.users.urls')),

    url(r'^static/(?P<path>.*)$', forceauth.exempt(serve), {'document_root': settings.MEDIA_ROOT}),
    url(r'^trigger500/$', lambda request: 1/0),
    url(r'^bugshot/', include('ecs.bugshot.urls')),
    url(r'^search/', include('haystack.urls')),
    url(r'^test/', direct_to_template, {'template': 'test.html'}),
    #url(r'^tests/killableprocess/$', 'ecs.utils.tests.killableprocess.timeout_view'),
    
)

