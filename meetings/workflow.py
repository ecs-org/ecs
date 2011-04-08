# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings

from ecs.workflow import Activity, guard, register
from ecs.meetings.models import Meeting
from ecs.communication.utils import send_system_message_template

register(Meeting)


class MeetingAgendaPreparation(Activity):
    class Meta:
        model = Meeting
        
    def get_url(self):
        return reverse('ecs.meetings.views.timetable_editor', kwargs={'meeting_pk': self.workflow.data.pk})

    def pre_perform(self, choice):
        m = self.workflow.data
        for recipient in settings.AGENDA_RECIPIENT_LIST:
            send_system_message_template(recipient, _('Invitation to meeting'), 'meetings/boardmember_invitation.txt', {'meeting': m})


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


class MeetingExpertAssignment(Activity):
    class Meta:
        model = Meeting

    def get_url(self):
        return reverse('ecs.meetings.views.expert_assignment_edit', kwargs={'meeting_pk': self.workflow.data.pk})

