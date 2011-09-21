# -*- coding: utf-8 -*-

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
        (u'August 2011 Sitzung',    (2011,  8,  2, 10, 0), (2011,  7,  6, 23, 59), (2011,  6, 30, 23, 59)),
        (u'September 2011 Sitzung', (2011,  9,  6, 10, 0), (2011,  8,  3, 23, 59), (2011,  7, 27, 23, 59)),
        (u'Oktober 2011 Sitzung',   (2011, 10,  4, 10, 0), (2011,  9,  7, 23, 59), (2011,  8, 31, 23, 59)),
        (u'November 2011 Sitzung',  (2011, 11,  8, 10, 0), (2011, 10, 12, 23, 59), (2011, 10,  5, 23, 59)),
        (u'Dezember 2011 Sitzung',  (2011, 12,  6, 10, 0), (2011, 11,  9, 23, 59), (2011, 11,  3, 23, 59)),

        (u'Januar 2012 Sitzung',    (2012,  1, 10, 10, 0), (2011, 12, 14, 23, 59), (2011, 12,  7, 23, 59)),
        (u'Februar 2012 Sitzung',   (2012,  2, 14, 10, 0), (2012,  1, 11, 23, 59), (2012,  1,  5, 23, 59)),
        (u'März 2012 Sitzung',      (2012,  3, 13, 10, 0), (2012,  2, 15, 23, 59), (2012,  2,  8, 23, 59)),
        (u'April 2012 Sitzung',     (2012,  4, 17, 10, 0), (2012,  3, 21, 23, 59), (2012,  3, 14, 23, 59)),
        (u'Mai 2012 Sitzung',       (2012,  5, 15, 10, 0), (2012,  4, 18, 23, 59), (2012,  4, 11, 23, 59)),
        (u'Juni 2012 Sitzung',      (2012,  6, 12, 10, 0), (2012,  5, 16, 23, 59), (2012,  5,  9, 23, 59)),
        (u'Juli 2012 Sitzung',      (2012,  7, 10, 10, 0), (2012,  6, 13, 23, 59), (2012,  6,  6, 23, 59)),
        
    )

    for m in meetings:
        meeting, created = Meeting.objects.get_or_create(start=datetime.datetime(*m[1]))
        meeting.title = m[0]
        meeting.deadline = datetime.datetime(*m[2])
        meeting.deadline_diplomathesis = datetime.datetime(*m[3])
        meeting.save()
