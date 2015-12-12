from ecs import workflow
from ecs.integration.django_workarounds import workaround_16759


def _patch_django():
    workaround_16759()
    

def startup():
    _patch_django()

    workflow.autodiscover() # discover workflow items

    import ecs.core.triggers
    import ecs.votes.triggers
    import ecs.notifications.triggers
    import ecs.meetings.triggers
