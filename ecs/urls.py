from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from django.shortcuts import render
from django.views.generic.base import RedirectView

from ecs.utils import forceauth

def handler500(request):
    ''' 500 error handler which includes ``request`` in the context '''
    from django.template import loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html') # You need to create a 500.html template.
    return HttpResponseServerError(t.render({'request': request}))


urlpatterns = [
    # Default redirect is same as redirect from login if no redirect is set (/dashboard/)
    url(r'^$', RedirectView.as_view(url=settings.LOGIN_REDIRECT_URL, permanent=False)),

    url(r'^', include('ecs.users.urls')),
    url(r'^core/', include('ecs.core.urls')),
    url(r'^docstash/', include('ecs.docstash.urls')),
    url(r'^checklist/', include('ecs.checklists.urls')),
    url(r'^vote/', include('ecs.votes.urls')),
    url(r'^dashboard/', include('ecs.dashboard.urls')),
    url(r'^task/', include('ecs.tasks.urls')),
    url(r'^communication/', include('ecs.communication.urls')),
    url(r'^billing/', include('ecs.billing.urls')),
    url(r'^boilerplate/', include('ecs.boilerplate.urls')),
    url(r'^scratchpad/', include('ecs.scratchpad.urls')),
    url(r'^document/', include('ecs.documents.urls')),
    url(r'^meeting/', include('ecs.meetings.urls')),
    url(r'^notification/', include('ecs.notifications.urls')),
    url(r'^signature/', include('ecs.signature.urls')),
    url(r'^statistics/', include('ecs.statistics.urls')),
    url(r'^tags/', include('ecs.tags.urls')),
    url(r'^', include('ecs.pki.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', forceauth.exempt(serve), {'document_root': settings.STATIC_ROOT}),
]


# XXX: do not bind to settings.DEBUG, to test working sentry on DEBUG:False
if 'ecs.userswitcher' in settings.INSTALLED_APPS:
    from django.http import HttpResponse
    import logging

    logger = logging.getLogger(__name__)

    @forceauth.exempt
    def _trigger_log(request):
        logger.warn('debug test message')
        return HttpResponse()

    @forceauth.exempt
    def _403(request):
        return render(request, '403.html', status=403)

    @forceauth.exempt
    def _404(request):
        return render(request, '404.html', status=404)

    @forceauth.exempt
    def _500(request):
        return render(request, '500.html', status=500)

    urlpatterns += [
        url(r'^debug/403/$', _403),
        url(r'^debug/404/$', _404),
        url(r'^debug/500/$', _500),
        url(r'^debug/trigger-log/$', _trigger_log),
    ]

if 'ecs.userswitcher' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^userswitcher/', include('ecs.userswitcher.urls')),
    ]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]
