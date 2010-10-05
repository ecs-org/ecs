from django.contrib.contenttypes.models import ContentType

from ecs.workflow.models import Workflow, Token, Node, NODE_TYPE_CATEGORY_ACTIVITY
from ecs.workflow.exceptions import BadActivity

class ObjectWorkflow(object):
    def __init__(self, obj):
        self.object = obj
        self.workflows = Workflow.objects.filter(
            content_type=ContentType.objects.get_for_model(type(obj)), 
            data_id=obj.pk,
        )

    def _get_activity_tokens(self, *acts):
        tokens = Token.objects.filter(workflow__in=self.workflows.values('pk').query, consumed_at=None, node__node_type__category=NODE_TYPE_CATEGORY_ACTIVITY).select_related('node', 'workflow')
        if acts:
            tokens = tokens.filter(node__node_type__in=[act._meta.node_type for act in acts])
        return tokens

    def _get_activities(self, *acts):
        return [token.node.bind(token.workflow) for token in self._get_activity_tokens(*acts)]

    activities = property(_get_activities)
    activitiy_tokens = property(_get_activity_tokens)

    def iter_controllers(self, activity, data=None):
        if isinstance(activity, Token):
            assert activity.workflow.data == self.object
            yield activity.node.bind(activity.workflow)
        else:
            for workflow in self.workflows.select_related('graph'):
                nodes = workflow.graph.nodes.filter(node_type=activity._meta.node_type)
                if data:
                    nodes = nodes.filter(data_id=data.pk, data_ct=ContentType.objects.get_for_model(type(data)))
                else:
                    nodes = nodes.filter(node_type__data_type=None)
                for node in nodes:
                    yield node.bind(workflow)

    def do(self, activity, data=None, choice=None):
        controllers = list(self.iter_controllers(activity, data=data))
        for a in controllers:
            a.perform(choice=choice)
        if not controllers:
            raise BadActivity(activity)

    def unlock(self, activity):
        for workflow in self.workflows.all():
            for node in Node.objects.filter(tokens__workflow=workflow, node_type=activity._meta.node_type):
                node.bind(workflow).unlock()

class WorkflowDescriptor(object):
    def __get__(self, obj, obj_type=None):
        return ObjectWorkflow(obj)
