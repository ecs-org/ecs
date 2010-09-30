from ecs import bootstrap
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.workflow.utils import setup_workflow_graph

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync',))
def meeting_workflow():
    from ecs.meetings.models import Meeting
    from ecs.meetings.workflow import MeetingAgendaPreparation, MeetingAgendaSending, MeetingDay, MeetingProtocolSending

    setup_workflow_graph(Meeting, 
        auto_start=True, 
        nodes={
            'meeting_agenda_generation': Args(MeetingAgendaPreparation, start=True),
            'meeting_agenda_sending': Args(MeetingAgendaSending),
            'meeting_day': Args(MeetingDay),
            'meeting_protocol_sending': Args(MeetingProtocolSending, end=True),
        }, 
        edges={
            ('meeting_agenda_generation', 'meeting_agenda_sending'): None,
            ('meeting_agenda_sending', 'meeting_day'): None,
            ('meeting_day', 'meeting_protocol_sending'): None,
        }
    )

