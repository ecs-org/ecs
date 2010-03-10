from django.conf.urls.defaults import *

import settings

# setup databrowse for debugging
from django.contrib import databrowse
from core import models
for m in ("Workflow", "Document", "EthicsCommission", 
          "SubmissionForm", "Investigator","InvestigatorEmployee",
          "NonTestedUsedDrug", "ForeignParticipatingCenter",
          "Amendment",
          "BaseNotificationForm", "ExtendedNotificationForm", "Checklist",
          "VoteReview", "Vote", "SubmissionReview", "Submission", 
          "NotificationAnswer",
          "Meeting", "User"):
    databrowse.site.register(getattr(models, m))

# enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/core/'}),

    url(r'^core/', include('core.urls')),
    url(r'^docstash/', include('docstash.urls')),
    
    #url(r'^tests/killableprocess/$', 'ecs.utils.tests.killableprocess.timeout_view'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^databrowse/(.*)', databrowse.site.root),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)
