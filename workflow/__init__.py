from django.db.models.signals import post_save, class_prepared
from django.contrib.contenttypes.models import ContentType
from ecs.workflow.controller import activity, control, guard
from ecs.workflow import patterns

__registry = set()

def register(model):
    if model in __registry:
        return
    __registry.add(model)
    from ecs.workflow.descriptors import WorkflowDescriptor
    model.workflow = WorkflowDescriptor()

def _post_save(sender, **kwargs):
    if sender not in __registry:
        return
    if kwargs['created']:
        from ecs.workflow.models import Workflow, Graph
        ct = ContentType.objects.get_for_model(sender)
        graphs = Graph.objects.filter(content_type=ct, auto_start=True)
        for graph in graphs:
            wf = Workflow.objects.create(graph=graph, data=kwargs['instance'])
            wf.start()
post_save.connect(_post_save)


    