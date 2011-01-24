from django.core.urlresolvers import reverse
from ecs.workflow import Activity, guard
from ecs.meetings.models import Meeting


class MeetingAgendaPreparation(Activity):
    class Meta:
        model = Meeting
        
    def get_url(self):
        return reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': self.workflow.data.pk})
        

class MeetingAgendaSending(Activity):
    class Meta:
        model = Meeting
        
    def get_url(self):
        return reverse('ecs.meetings.views.agenda_htmlemail', kwargs={'meeting_pk': self.workflow.data.pk})


class MeetingDay(Activity):
    class Meta:
        model = Meeting
        
    def is_locked(self):
        return not bool(self.workflow.data.ended)
        
    def get_url(self):
        return reverse('ecs.meetings.views.meeting_assistant', kwargs={'meeting_pk': self.workflow.data.pk})


class MeetingProtocolSending(Activity):
    class Meta:
        model = Meeting

    pass