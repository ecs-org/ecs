from django.conf.urls import url

from ecs.meetings import views


urlpatterns = (
    url(r'^reschedule/submission/(?P<submission_pk>\d+)/', views.reschedule_submission),

    url(r'^new/$', views.create_meeting),
    url(r'^next/$', views.next),
    url(r'^list/upcoming/$', views.upcoming_meetings),
    url(r'^list/past/$', views.past_meetings),
    url(r'^(?P<meeting_pk>\d+)/$', views.meeting_details),
    url(r'^(?P<meeting_pk>\d+)/constraints_for_user/(?P<user_pk>\d+)/$', views.edit_user_constraints),
    url(r'^(?P<meeting_pk>\d+)/edit/$', views.edit_meeting),
    url(r'^(?P<meeting_pk>\d+)/open_tasks/$', views.open_tasks),
    url(r'^(?P<meeting_pk>\d+)/tops/$', views.tops),
    url(r'^(?P<meeting_pk>\d+)/submissions/$', views.submission_list),
    url(r'^(?P<meeting_pk>\d+)/documents/zip/$', views.download_zipped_documents),
    url(r'^(?P<meeting_pk>\d+)/documents/(?P<submission_pk>\d+)/zip/$', views.download_zipped_documents),

    url(r'^(?P<meeting_pk>\d+)/timetable/$', views.timetable_editor),
    url(r'^(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/$', views.optimize_timetable),
    url(r'^(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/long/$', views.optimize_timetable_long),
    url(r'^(?P<meeting_pk>\d+)/timetable/entry/new/$', views.add_timetable_entry),
    url(r'^(?P<meeting_pk>\d+)/timetable/entry/add/$', views.add_free_timetable_entry),
    url(r'^(?P<meeting_pk>\d+)/timetable/entry/move/$', views.move_timetable_entry),
    url(r'^(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/delete/$', views.remove_timetable_entry),
    url(r'^(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/update/$', views.update_timetable_entry),
    url(r'^(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/users/(?P<user_pk>\d+)/toggle/$', views.toggle_participation),

    url(r'^(?P<meeting_pk>\d+)/assistant/$', views.meeting_assistant),
    url(r'^(?P<meeting_pk>\d+)/assistant/start/$', views.meeting_assistant_start),
    url(r'^(?P<meeting_pk>\d+)/assistant/stop/$', views.meeting_assistant_stop),
    url(r'^(?P<meeting_pk>\d+)/assistant/(?P<top_pk>\d+)/$', views.meeting_assistant_top),
    url(r'^(?P<meeting_pk>\d+)/assistant/quickjump/$', views.meeting_assistant_quickjump),
    url(r'^(?P<meeting_pk>\d+)/assistant/comments/$', views.meeting_assistant_comments),
    url(r'^(?P<meeting_pk>\d+)/assistant/retrospective_thesis_expedited/$', views.meeting_assistant_retrospective_thesis_expedited),

    url(r'^(?P<meeting_pk>\d+)/agenda/pdf/$', views.agenda_pdf),
    url(r'^(?P<meeting_pk>\d+)/agenda/send/$', views.send_agenda_to_board),
    url(r'^(?P<meeting_pk>\d+)/expedited_reviewer_invitations/send/$', views.send_expedited_reviewer_invitations),
    url(r'^(?P<meeting_pk>\d+)/timetable_pdf/$', views.timetable_pdf),
    url(r'^(?P<meeting_pk>\d+)/timetablepart/$', views.timetable_htmlemailpart),
    url(r'^(?P<meeting_pk>\d+)/protocol/edit/$', views.edit_protocol),
    url(r'^(?P<meeting_pk>\d+)/protocol/pdf/$', views.protocol_pdf),
    url(r'^(?P<meeting_pk>\d+)/protocol/send/$', views.send_protocol),
)
