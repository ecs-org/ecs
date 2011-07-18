from django.contrib.contenttypes.models import ContentType
from ecs.tasks.models import Task

def get_obj_tasks(user, activities, obj, data=None):
    tasks = Task.objects.filter(workflow_token__in=obj.workflow.tokens.filter(node__node_type__in=[a._meta.node_type for a in activities]).values('pk').query, deleted_at=None)
    if data:
        tasks = tasks.filter(workflow_token__node__data_id=data.pk, workflow_token__node__data_ct=ContentType.objects.get_for_model(type(data)))
    return tasks
