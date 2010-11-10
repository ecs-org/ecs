from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('ecs.meetings.views',
    url(r'^users/by_medical_category/$', 'users_by_medical_category'),
    url(r'^submission/(?P<submission_pk>\d+)/schedule/', 'schedule_submission'),

    url(r'^meeting/new/$', 'create_meeting'),
    #url(r'^meeting/(?P<meeting_pk>\d+)/$', 'view_meeting'),
    url(r'^meetings/$', 'meeting_list'),
    url(r'^meeting/(?P<meeting_pk>\d+)/particiaptions/$', 'participation_editor'),
    url(r'^meeting/(?P<meeting_pk>\d+)/medical_categories/$', 'medical_categories'),
    #url(r'^meeting/(?P<meeting_pk>\d+)/medical_categories/(?P<category_pk>\d+)/$', 'medical_categories'),
    url(r'^meeting/(?P<meeting_pk>\d+)/constraints_for_user/(?P<user_pk>\d+)/$', 'edit_user_constraints'),

    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/editor/$', 'timetable_editor'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/optimize/(?P<algorithm>random|brute_force|ga)/$', 'optimize_timetable'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/new/$', 'add_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/add/$', 'add_free_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/move/$', 'move_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/delete/$', 'remove_timetable_entry'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable/entry/(?P<entry_pk>\d+)/update/$', 'update_timetable_entry'),

    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/$', 'meeting_assistant'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/clear/$', 'meeting_assistant_clear'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/start/$', 'meeting_assistant_start'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/stop/$', 'meeting_assistant_stop'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/(?P<top_pk>\d+)/$', 'meeting_assistant_top'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/quickjump/$', 'meeting_assistant_quickjump'),
    url(r'^meeting/(?P<meeting_pk>\d+)/assistant/comments/$', 'meeting_assistant_comments'),

    url(r'^meeting/(?P<meeting_pk>\d+)/agenda_pdf/$', 'agenda_pdf'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetable_pdf/$', 'timetable_pdf'),
    url(r'^meeting/(?P<meeting_pk>\d+)/agenda_htmlemail/$', 'agenda_htmlemail'),
    url(r'^meeting/(?P<meeting_pk>\d+)/timetablepart/$', 'timetable_htmlemailpart'),
    url(r'^meeting/(?P<meeting_pk>\d+)/protocol_pdf/$', 'protocol_pdf'),
)
