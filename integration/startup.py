from ecs import workflow

def startup():
    workflow.autodiscover() # discover workflow items

    import ecs.core.triggers
    import ecs.votes.triggers
    import ecs.notifications.triggers