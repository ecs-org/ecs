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

    url(r'^notification/new/$', 'ecs.core.views.select_notification_creation_type'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/$', 'ecs.core.views.view_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'ecs.core.views.notification_pdf'),
    url(r'^notification/(?P<notification_pk>\d+)/xhtml2pdf/$', 'ecs.core.views.notification_xhtml2pdf'),
    url(r'^notifications/$', 'ecs.core.views.notification_list'),
    url(r'^submission_data_for_notification/$', 'ecs.core.views.submission_data_for_notification'),

    url(r'^document/(?P<document_pk>\d+)/download/$', 'ecs.core.views.download_document'),

    url(r'^submission_form/(?P<submission_form_pk>\d+)/$', 'ecs.core.views.view_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/pdf/$', 'ecs.core.views.submission_pdf'),
    url(r'^submission_form/new/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_submission_form'),
    url(r'^submission_forms/$', 'ecs.core.views.submission_form_list'),
    
    url(r'^meeting/new/$', 'ecs.core.views.create_meeting'),
    #url(r'^meeting/(?P<meeting_pk>\d+)/$', 'ecs.core.views.view_meeting'),
    url(r'^meetings/$', 'ecs.core.views.meeting_list'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/editor/$', 'ecs.core.views.timetable_editor'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/new/$', 'ecs.core.views.add_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/move/$', 'ecs.core.views.move_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/delete/$', 'ecs.core.views.remove_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/constraints_for_user/(?P<user_pk>\d+)/$', 'ecs.core.views.meetings.edit_user_constraints'),

)
