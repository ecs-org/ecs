from django.conf.urls.defaults import *

import settings

# setup databrowse for debugging
from django.contrib import databrowse
from ecs.core.models import Workflow, Document, EthicsCommission,\
    InvolvedCommissionsForSubmission, InvolvedCommissionsForNotification,\
    SubmissionForm,Investigator,InvestigatorEmployee,TherapiesApplied,\
    DiagnosticsApplied,NonTestedUsedDrugs,ParticipatingCenter,Amendment,\
    NotificationForm,Checklist,SubmissionSet,NotificationSet,VoteReview,\
    Vote,SubmissionReview,Submission,NotificationAnswer,Notification,Meeting,\
    User 
for m in ("Workflow", "Document", "EthicsCommission", 
    "InvolvedCommissionsForSubmission","InvolvedCommissionsForNotification",
    "SubmissionForm","Investigator","InvestigatorEmployee","TherapiesApplied",
    "DiagnosticsApplied","NonTestedUsedDrugs","ParticipatingCenter","Amendment",
    "NotificationForm","Checklist","SubmissionSet","NotificationSet",
    "VoteReview","Vote","SubmissionReview","Submission","NotificationAnswer",
    "Notification","Meeting","User"):
    exec "databrowse.site.register(%s)" % m

# enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    (r'^core/$', 'ecs.core.views.index'),
    (r'^demo','ecs.core.views.demo'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Enable databrowse
    (r'^databrowse/(.*)', databrowse.site.root),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)
