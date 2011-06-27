from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.meetings.views',
    url(r'^users/by_medical_category/$', 'users_by_medical_category'),
    url(r'^submission/(?P<submission_pk>\d+)/reschedule/', 'reschedule_submission'),

    url(r'^meeting/next/$', 'next'),
    url(r'^meeting/new/$', 'create_meeting'),
    #url(r'^meeting/(?P<meeting_pk>\d+)/$', 'view_meeting'),
    url(r'^meetings/upcoming/$', 'upcoming_meetings'),
    url(r'^meetings/past/$', 'past_meetings'),
    url(r'^meeting/(?P<meeting_pk>\d+)/experts/$', 'expert_assignment'),
    #url(r'^meeting/(?P<meeting_pk>\d+)/medical_categories/(?P<category_pk>\d+)/$', 'medical_categories'),
    url(r'^meeting/(?P<meeting_pk>\d+)/constraints_for_user/(?P<user_pk>\d+)/$', 'edit_user_constraints'),
    url(r'^meeting/(?P<meeting_pk>\d+)/status/$', 'status'),

    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/$', 'timetable_editor'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/$', 'optimize_timetable'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/new/$', 'add_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/add/$', 'add_free_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/move/$', 'move_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/delete/$', 'remove_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/update/$', 'update_timetable_entry'),

    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/$', 'meeting_assistant'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/start/$', 'meeting_assistant_start'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/stop/$', 'meeting_assistant_stop'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/(?P<top_pk>\d+)/$', 'meeting_assistant_top'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/quickjump/$', 'meeting_assistant_quickjump'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/comments/$', 'meeting_assistant_comments'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/retrospective_thesis_expedited/$', 'meeting_assistant_retrospective_thesis_expedited'),

    url(r'^meeting/(?P<meeting_pk>\d+)/agenda_pdf/$', 'agenda_pdf'),
    url(r'^meeting/(?P<meeting_pk>\d+)/send_agenda_to_board/$', 'send_agenda_to_board'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable_pdf/$', 'timetable_pdf'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetablepart/$', 'timetable_htmlemailpart'),
    url(r'^meeting/(?P<meeting_pk>\d+)/protocol_pdf/$', 'protocol_pdf'),
    
    url(r'^meeting/(?P<meeting_pk>\d+)/votes_signing/$', 'votes_signing'),
)
