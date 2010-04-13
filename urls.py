from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login
from django.views.static import serve
from ecs.utils import forceauth
import django

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/core/'}),

    url(r'^core/', include('core.urls')),
    url(r'^docstash/', include('docstash.urls')),
    url(r'^accounts/login/$', forceauth.exempt(login), {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^feedback/', include("feedback.urls")),

    url(r'^static/(?P<path>.*)$', forceauth.exempt(serve), {'document_root': settings.MEDIA_ROOT}),

    #url(r'^tests/killableprocess/$', 'ecs.utils.tests.killableprocess.timeout_view'),
)

