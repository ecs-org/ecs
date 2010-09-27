from django.contrib.contenttypes.models import ContentType
from ecs.utils import cached_property

from ecs.workflow.controllers.registry import add_guard

class GuardOptions(object):
    def __init__(self, func, model=None):
        self.name = add_guard(func)
        self.model = model

    @cached_property
    def instance(self):
        from ecs.workflow.models import Guard
        if self.model:
            ct = ContentType.objects.get_for_model(self.model)
        else:
            ct = None
        try:
            return Guard.objects.get(content_type=ct, implementation=self.name)
        except Guard.DoesNotExist:
            raise RuntimeError("Guard %s is not synced to the database. Forgot to run the workflow_sync command?" % self.name)


def guard(func=None, model=None):
    def decorator(func):
        func._meta = GuardOptions(func, model)
        return func
    if not func:
        return decorator
    else:
        return decorator(func)


class EdgeController(object):
    def __init__(self, edge, workflow):
        self.edge = edge
        self.workflow = workflow
    
    to_node = property(lambda self: self.edge.to_node.bind(self.workflow))
    from_node = property(lambda self: self.edge.from_node.bind(self.workflow))
    deadline = property(lambda self: self.edge.deadline)
    negated = property(lambda self: self.edge.negated)
    guard = property(lambda self: self.edge.bind_guard(self.workflow))
    
    def is_active(self):
        return self.negated != self.guard()


