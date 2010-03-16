from django.conf.urls.defaults import *

import settings

# setup databrowse for debugging
"""from django.contrib import databrowse
from core import models
for m in ("Document", "EthicsCommission", 
          "Submission", "SubmissionForm", "Investigator","InvestigatorEmployee", "NonTestedUsedDrug", "ForeignParticipatingCenter",
          "Notification", "ProgressReportNotification", "CompletionReportNotification",
          "Amendment", "Checklist", "Workflow",
          "VoteReview", "Vote", "SubmissionReview",
          "NotificationAnswer",
          "Meeting", "User"):
    databrowse.site.register(getattr(models, m))
"""

# enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/core/'}),

    url(r'^core/', include('core.urls')),
    url(r'^docstash/', include('docstash.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    
    #url(r'^tests/killableprocess/$', 'ecs.utils.tests.killableprocess.timeout_view'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^databrowse/(.*)', databrowse.site.root),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)
