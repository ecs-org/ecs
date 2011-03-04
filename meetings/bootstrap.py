import datetime
from decimal import Decimal

from ecs import bootstrap
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph


# for marking the task names translatable
_ = lambda s: s

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync',))
def meeting_workflow():
    from ecs.meetings.models import Meeting
    from ecs.meetings.workflow import MeetingAgendaPreparation, MeetingAgendaSending, MeetingDay, MeetingProtocolSending

    setup_workflow_graph(Meeting, 
        auto_start=True, 
        nodes={
            'meeting_agenda_generation': Args(MeetingAgendaPreparation, start=True, name=_("Meeting Agenda Generation")),
            'meeting_agenda_sending': Args(MeetingAgendaSending, name=_("Meeting Agenda Sending")),
            'meeting_day': Args(MeetingDay, name=_("Meeting Day")),
            'meeting_protocol_sending': Args(MeetingProtocolSending, end=True, name=_("Meeting Protocol Sending")),
        }, 
        edges={
            ('meeting_agenda_generation', 'meeting_agenda_sending'): None,
            ('meeting_agenda_sending', 'meeting_day'): None,
            ('meeting_day', 'meeting_protocol_sending'): None,
        }
    )


@bootstrap.register(depends_on=('ecs.meetings.bootstrap.meeting_workflow',))
def meetings_create():
    from ecs.meetings.models import AssignedMedicalCategory
    from ecs.meetings.models import Meeting

    meetings_meeting_1, created = Meeting.objects.get_or_create(start = datetime.datetime(2010, 8, 3, 10, 0))
    meetings_meeting_1.title = u'Aug Meeting'
    meetings_meeting_1.optimization_task_id = None
    meetings_meeting_1.started = None
    meetings_meeting_1.ended = None
    meetings_meeting_1.comments = None
    meetings_meeting_1.deadline = datetime.datetime(2010, 7, 7, 0, 0)
    meetings_meeting_1.deadline_diplomathesis = datetime.datetime(2010, 6, 30, 0, 0)
    meetings_meeting_1.save()

    meetings_meeting_2, created = Meeting.objects.get_or_create(start = datetime.datetime(2010, 9, 7, 10, 0))
    meetings_meeting_2.title = u'Sep Meeting'
    meetings_meeting_2.optimization_task_id = None
    meetings_meeting_2.started = None
    meetings_meeting_2.ended = None
    meetings_meeting_2.comments = None
    meetings_meeting_2.deadline = datetime.datetime(2010, 8, 4, 0, 0)
    meetings_meeting_2.deadline_diplomathesis = datetime.datetime(2010, 7, 28, 0, 0)
    meetings_meeting_2.save()

    meetings_meeting_3, created = Meeting.objects.get_or_create(start = datetime.datetime(2010, 10, 5, 10, 0))
    meetings_meeting_3.title = u'Oct Meeting'
    meetings_meeting_3.optimization_task_id = None
    meetings_meeting_3.started = None
    meetings_meeting_3.ended = None
    meetings_meeting_3.comments = None
    meetings_meeting_3.deadline = datetime.datetime(2010, 9, 8, 0, 0)
    meetings_meeting_3.deadline_diplomathesis = datetime.datetime(2010, 9, 1, 0, 0)
    meetings_meeting_3.save()

    meetings_meeting_4, created = Meeting.objects.get_or_create(start = datetime.datetime(2010, 11, 9, 10, 0))
    meetings_meeting_4.title = u'Nov Meeting'
    meetings_meeting_4.optimization_task_id = None
    meetings_meeting_4.started = None
    meetings_meeting_4.ended = None
    meetings_meeting_4.comments = None
    meetings_meeting_4.deadline = datetime.datetime(2010, 10, 13, 0, 0)
    meetings_meeting_4.deadline_diplomathesis = datetime.datetime(2010, 10, 6, 0, 0)
    meetings_meeting_4.save()

    meetings_meeting_5, created = Meeting.objects.get_or_create(start = datetime.datetime(2010, 12, 7, 10, 0))
    meetings_meeting_5.title = u'Dec Meeting'
    meetings_meeting_5.optimization_task_id = None
    meetings_meeting_5.started = None
    meetings_meeting_5.ended = None
    meetings_meeting_5.comments = None
    meetings_meeting_5.deadline = datetime.datetime(2010, 11, 10, 0, 0)
    meetings_meeting_5.deadline_diplomathesis = datetime.datetime(2010, 11, 3, 0, 0)
    meetings_meeting_5.save()

    meetings_meeting_6, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 1, 11, 10, 0))
    meetings_meeting_6.title = u'Jan Meeting'
    meetings_meeting_6.optimization_task_id = None
    meetings_meeting_6.started = None
    meetings_meeting_6.ended = None
    meetings_meeting_6.comments = None
    meetings_meeting_6.deadline = datetime.datetime(2010, 12, 15, 0, 0)
    meetings_meeting_6.deadline_diplomathesis = datetime.datetime(2010, 12, 9, 0, 0)
    meetings_meeting_6.save()

    meetings_meeting_7, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 2, 15, 10, 0))
    meetings_meeting_7.title = u'Feb Meeting'
    meetings_meeting_7.optimization_task_id = None
    meetings_meeting_7.started = None
    meetings_meeting_7.ended = None
    meetings_meeting_7.comments = None
    meetings_meeting_7.deadline = datetime.datetime(2011, 1, 12, 0, 0)
    meetings_meeting_7.deadline_diplomathesis = datetime.datetime(2011, 1, 5, 0, 0)
    meetings_meeting_7.save()

    meetings_meeting_8, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 3, 15, 10, 0))
    meetings_meeting_8.title = u'Mar Meeting'
    meetings_meeting_8.optimization_task_id = None
    meetings_meeting_8.started = None
    meetings_meeting_8.ended = None
    meetings_meeting_8.comments = None
    meetings_meeting_8.deadline = datetime.datetime(2011, 2, 16, 0, 0)
    meetings_meeting_8.deadline_diplomathesis = datetime.datetime(2011, 2, 9, 0, 0)
    meetings_meeting_8.save()

    meetings_meeting_9, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 4, 12, 10, 0))
    meetings_meeting_9.title = u'Apr Meeting'
    meetings_meeting_9.optimization_task_id = None
    meetings_meeting_9.started = None
    meetings_meeting_9.ended = None
    meetings_meeting_9.comments = None
    meetings_meeting_9.deadline = datetime.datetime(2011, 3, 16, 0, 0)
    meetings_meeting_9.deadline_diplomathesis = datetime.datetime(2011, 3, 9, 0, 0)
    meetings_meeting_9.save()

    meetings_meeting_10, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 5, 10, 10, 0))
    meetings_meeting_10.title = u'May Meeting'
    meetings_meeting_10.optimization_task_id = None
    meetings_meeting_10.started = None
    meetings_meeting_10.ended = None
    meetings_meeting_10.comments = None
    meetings_meeting_10.deadline = datetime.datetime(2011, 4, 13, 0, 0)
    meetings_meeting_10.deadline_diplomathesis = datetime.datetime(2011, 4, 6, 0, 0)
    meetings_meeting_10.save()

    meetings_meeting_11, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 6, 7, 10, 0))
    meetings_meeting_11.title = u'Jun Meeting'
    meetings_meeting_11.optimization_task_id = None
    meetings_meeting_11.started = None
    meetings_meeting_11.ended = None
    meetings_meeting_11.comments = None
    meetings_meeting_11.deadline = datetime.datetime(2011, 5, 11, 0, 0)
    meetings_meeting_11.deadline_diplomathesis = datetime.datetime(2011, 5, 4, 0, 0)
    meetings_meeting_11.save()

    meetings_meeting_12, created = Meeting.objects.get_or_create(start = datetime.datetime(2011, 7, 5, 10, 0))
    meetings_meeting_12.title = u'Jul Meeting'
    meetings_meeting_12.optimization_task_id = None
    meetings_meeting_12.started = None
    meetings_meeting_12.ended = None
    meetings_meeting_12.comments = None
    meetings_meeting_12.deadline = datetime.datetime(2011, 6, 8, 0, 0)
    meetings_meeting_12.deadline_diplomathesis = datetime.datetime(2011, 6, 1, 0, 0)
    meetings_meeting_12.save()
