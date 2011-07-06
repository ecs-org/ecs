import datetime
from decimal import Decimal

from ecs import bootstrap
from ecs.utils import Args
from ecs.workflow.patterns import Generic
from ecs.integration.utils import setup_workflow_graph
from ecs.workflow.patterns import Generic


@bootstrap.register()
def meetings_create():
    from ecs.meetings.models import AssignedMedicalCategory
    from ecs.meetings.models import Meeting

    meetings = (
        ('Jun Meeting', (2011,  6,  7, 10, 0), (2011,  5, 11, 0, 0), (2011,  5,  4, 0, 0)),
        ('Jul Meeting', (2011,  7,  5, 10, 0), (2011,  6,  8, 0, 0), (2011,  6,  1, 0, 0)),
        ('August Sitzung',    (2011,  8,  3, 10, 0), (2011,  7,  7, 23, 59), (2011,  6, 30, 23, 59)),
        ('September Sitzung', (2011,  9,  7, 10, 0), (2011,  8,  4, 23, 59), (2011,  7, 28, 23, 59)),
        ('Oktober Sitzung',   (2011, 10,  5, 10, 0), (2011,  9,  8, 23, 59), (2011,  9,  1, 23, 59)),
        ('November Sitzung',  (2011, 11,  9, 10, 0), (2011, 10, 13, 23, 59), (2011, 10,  6, 23, 59)),
        ('Dezember Sitzung',  (2011, 12,  7, 10, 0), (2011, 11, 10, 23, 59), (2011, 11,  3, 23, 59)),
    )

    for m in meetings:
        meeting, created = Meeting.objects.get_or_create(start=datetime.datetime(*m[1]))
        meeting.title = m[0]
        meeting.deadline = datetime.datetime(*m[2])
        meeting.deadline_diplomathesis = datetime.datetime(*m[3])
        meeting.save()

