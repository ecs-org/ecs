import datetime
from decimal import Decimal

from ecs import bootstrap
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.workflow.patterns import Generic


# for marking the task names translatable
_ = lambda s: s

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def meeting_workflow():
    from ecs.meetings.models import Meeting
    from ecs.meetings.workflow import MeetingAgendaPreparation, MeetingDay, MeetingProtocolSending, MeetingExpertAssignment

    OFFICE_GROUP = 'EC-Office'

    setup_workflow_graph(Meeting, 
        auto_start=True, 
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'meeting_expert_assignment': Args(MeetingExpertAssignment, group=OFFICE_GROUP, name=_('Meeting Expert Assignment')),
            'meeting_agenda_generation': Args(MeetingAgendaPreparation, group=OFFICE_GROUP, name=_("Meeting Agenda Generation")),
            'meeting_day': Args(MeetingDay, group=OFFICE_GROUP, name=_("Meeting Day")),
            'meeting_protocol_sending': Args(MeetingProtocolSending, group=OFFICE_GROUP, end=True, name=_("Meeting Protocol Sending")),
        }, 
        edges={
            ('start', 'meeting_expert_assignment'): None,
            ('meeting_expert_assignment', 'meeting_agenda_generation'): None,
            ('meeting_agenda_generation', 'meeting_day'): None,
            ('meeting_day', 'meeting_protocol_sending'): None,
        }
    )


@bootstrap.register(depends_on=('ecs.meetings.bootstrap.meeting_workflow',))
def meetings_create():
    from ecs.meetings.models import AssignedMedicalCategory
    from ecs.meetings.models import Meeting

    meetings = (
        ('Aug Meeting', (2010,  8,  3, 10, 0), (2010,  7,  7, 0, 0), (2010,  6, 30, 0, 0)),
        ('Sep Meeting', (2010,  9,  7, 10, 0), (2010,  8,  4, 0, 0), (2010,  7, 28, 0, 0)),
        ('Oct Meeting', (2010, 10,  5, 10, 0), (2010,  9,  8, 0, 0), (2010,  9,  1, 0, 0)),
        ('Nov Meeting', (2010, 11,  9, 10, 0), (2010, 10, 13, 0, 0), (2010, 10,  6, 0, 0)),
        ('Dec Meeting', (2010, 12,  7, 10, 0), (2010, 11, 10, 0, 0), (2010, 11,  3, 0, 0)),
        ('Jan Meeting', (2011,  1, 11, 10, 0), (2010, 12, 15, 0, 0), (2010, 12,  9, 0, 0)),
        ('Feb Meeting', (2011,  2, 15, 10, 0), (2011,  1, 12, 0, 0), (2011,  1,  5, 0, 0)),
        ('Mar Meeting', (2011,  3, 15, 10, 0), (2011,  2, 16, 0, 0), (2011,  2,  9, 0, 0)),
        ('Apr Meeting', (2011,  4, 12, 10, 0), (2011,  3, 16, 0, 0), (2011,  3,  9, 0, 0)),
        ('May Meeting', (2011,  5, 10, 10, 0), (2011,  4, 13, 0, 0), (2011,  4,  6, 0, 0)),
        ('Jun Meeting', (2011,  6,  7, 10, 0), (2011,  5, 11, 0, 0), (2011,  5,  4, 0, 0)),
        ('Jul Meeting', (2011,  7,  5, 10, 0), (2011,  6,  8, 0, 0), (2011,  6,  1, 0, 0)),
    )

    for m in meetings:
        meeting, created = Meeting.objects.get_or_create(start=datetime.datetime(*m[1]))
        meeting.title = m[0]
        meeting.deadline = datetime.datetime(*m[2])
        meeting.deadline_diplomathesis = datetime.datetime(*m[3])
        meeting.optimization_task_id = None
        meeting.started = None
        meeting.ended = None
        meeting.comments = None
        meeting.save()

