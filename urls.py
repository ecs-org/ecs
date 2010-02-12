from django.conf.urls.defaults import *

import settings

# setup databrowse for debugging
from django.contrib import databrowse
from core import models
for m in ("Workflow", "Document", "EthicsCommission", 
          "InvolvedCommissionsForSubmission",
          "InvolvedCommissionsForNotification",
          "SubmissionForm","Investigator","InvestigatorEmployee",
          "TherapiesApplied",
          "DiagnosticsApplied", "NonTestedUsedDrugs", "ParticipatingCenter",
          "Amendment",
          "NotificationForm", "Checklist", "SubmissionSet",
          "VoteReview", "Vote", "SubmissionReview", "Submission", 
          "NotificationAnswer",
          "Notification", "Meeting", "User"):
    databrowse.site.register(getattr(models, m))

# enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/core/submission/1/'}),
    (r'^welcome$', 'django.views.generic.simple.redirect_to', {'url': '/core/submission/1/'}),
    url(r'^core/', include('core.urls')),
    url(r'^demo','ecs.core.views.demo'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Enable databrowse
    url(r'^databrowse/(.*)', databrowse.site.root),

    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)
