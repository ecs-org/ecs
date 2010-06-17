from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    # Example:
    # (r'^ecs/', include('ecs.foo.urls')),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/dashboard/', 'permanent': True}),

    url(r'^notification/new/$', 'ecs.core.views.select_notification_creation_type'),
    url(r'^notification/new/(?P<notification_type_pk>\d+)/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/$', 'ecs.core.views.view_notification'),
    url(r'^notification/(?P<notification_pk>\d+)/pdf/$', 'ecs.core.views.notification_pdf'),
    url(r'^notifications/$', 'ecs.core.views.notification_list'),
    url(r'^submission_data_for_notification/$', 'ecs.core.views.submission_data_for_notification'),

    url(r'^document/(?P<document_pk>\d+)/download/$', 'ecs.core.views.download_document'),

    url(r'^submission/(?P<submission_pk>\d+)/edit/', 'ecs.core.views.edit_submission'),
    url(r'^submission/(?P<submission_pk>\d+)/start_workflow/', 'ecs.core.views.start_workflow'),
    url(r'^submission/(?P<submission_pk>\d+)/copy_form/', 'ecs.core.views.copy_latest_submission_form'),
    url(r'^submission/(?P<submission_pk>\d+)/schedule/', 'ecs.core.views.schedule_submission'),
    url(r'^submission/(?P<submission_pk>\d+)/messages/send/', 'ecs.messages.views.send_message'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/$', 'ecs.core.views.view_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/pdf/$', 'ecs.core.views.submission_pdf'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/copy/$', 'ecs.core.views.copy_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/readonly/$', 'ecs.core.views.readonly_submission_form'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/checklist/(?P<blueprint_pk>\d+)/$', 'ecs.core.views.checklist_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/executive/$', 'ecs.core.views.executive_review'),
    url(r'^submission_form/(?P<submission_form_pk>\d+)/review/thesis/$', 'ecs.core.views.retrospective_thesis_review'),
    url(r'^submission_form/new/(?:(?P<docstash_key>.+)/)?$', 'ecs.core.views.create_submission_form'),
    url(r'^submission_forms/$', 'ecs.core.views.submission_form_list'),
    
    url(r'^users/by_medical_category/$', 'ecs.core.views.users_by_medical_category'),
    
    url(r'^meeting/new/$', 'ecs.core.views.create_meeting'),
    #url(r'^meeting/(?P<meeting_pk>\d+)/$', 'ecs.core.views.view_meeting'),
    url(r'^meetings/$', 'ecs.core.views.meeting_list'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/editor/$', 'ecs.core.views.timetable_editor'),
    url(r'^meeting/(?P<meeting_pk>\d+)/particiaptions/$', 'ecs.core.views.participation_editor'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/$', 'ecs.core.views.optimize_timetable'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/new/$', 'ecs.core.views.add_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/add/$', 'ecs.core.views.add_free_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/move/$', 'ecs.core.views.move_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/delete/$', 'ecs.core.views.remove_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/update/$', 'ecs.core.views.update_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/constraints_for_user/(?P<user_pk>\d+)/$', 'ecs.core.views.meetings.edit_user_constraints'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/$', 'ecs.core.views.meeting_assistant'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/clear/$', 'ecs.core.views.meeting_assistant_clear'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/start/$', 'ecs.core.views.meeting_assistant_start'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/stop/$', 'ecs.core.views.meeting_assistant_stop'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/(?P<top_pk>\d+)/$', 'ecs.core.views.meeting_assistant_top'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/quickjump/$', 'ecs.core.views.meeting_assistant_quickjump'),

    url(r'^checklist/(?P<checklist_pk>\d+)/comments/(?P<flavour>positive|negative)/', 'ecs.core.views.checklist_comments'),
)
