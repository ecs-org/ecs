# -*- coding: utf-8 -*-

from ecs import bootstrap
from ecs.integration.utils import setup_workflow_graph
from ecs.utils import Args
from ecs.workflow.patterns import Generic


# for marking the task names translatable
_ = lambda s: s

@bootstrap.register(depends_on=('ecs.integration.bootstrap.workflow_sync', 'ecs.core.bootstrap.auth_groups'))
def user_workflow():
    from ecs.users.models import UserProfile
    from ecs.users.workflow import UserApproval
    from ecs.users.workflow import is_approved

    OFFICE_GROUP = 'EC-Office'

    setup_workflow_graph(UserProfile,
        auto_start=True,
        nodes={
            'start': Args(Generic, start=True, name=_("Start")),
            'office_approval': Args(UserApproval, name=_('User Approval'), group=OFFICE_GROUP),
            'end': Args(Generic, end=True, name=_("End")),
        },
        edges={
            ('start', 'end'): Args(guard=is_approved),
            ('start', 'office_approval'): Args(guard=is_approved, negated=True),
            ('office_approval', 'end'): None,
        }
    )

