from django.contrib.contenttypes.models import ContentType

from ecs.workflow import controller
from ecs.workflow.models import Workflow, Token, Node

class BoundActivity(object):
    def __init__(self, node, workflow):
        self.activity = controller.get_handler(node)
        self.workflow = workflow
        self.node = node

    def perform(self):
        self.activity.perform(self.node, self.workflow)
        
    def unlock(self):
        self.activity.unlock(self.node, self.workflow)

    def __repr__(self):
        return u"<BoundActivity %s in %s>" % (self.node, self.workflow)


class ObjectWorkflow(object):
    def __init__(self, obj):
        self.object = obj
        ct = ContentType.objects.get_for_model(type(obj))
        self.workflows = Workflow.objects.filter(content_type=ct, data_id=obj.pk)

    def _get_activity_tokens(self, *acts):
        tokens = Token.objects.filter(workflow__in=self.workflows.values('pk'), consumed_at=None, node__node_type__is_activity=True).select_related('node', 'workflow')
        if acts:
            tokens = tokens.filter(node__node_type__in=[act.node_type for act in acts])
        return tokens

    def _get_activities(self, *acts):
        return [BoundActivity(token.node, token.workflow) for token in self._get_activity_tokens(*acts)]

    activities = property(_get_activities)
    activitiy_tokens = property(_get_activity_tokens)

    def get(self, activity):
        token = self.get_token(activity)
        return BoundActivity(token.node, token.workflow)

    def get_token(self, activity):
        if isinstance(activity, Token):
            return activity
        try:
            return self._get_activity_tokens(activity)[:1].get()
        except Token.DoesNotExist:
            raise KeyError("no token for activity %s" % activity)

    def do(self, activity):
        self.get(activity).perform()

    def unlock(self, activity):
        for workflow in self.workflows:
            for node in Node.objects.filter(tokens__workflow=workflow, node_type=activity.node_type):
                node.unlock(workflow)

class WorkflowDescriptor(object):
    def __get__(self, obj, obj_type=None):
        return ObjectWorkflow(obj)
