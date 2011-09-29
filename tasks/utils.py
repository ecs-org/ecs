from functools import wraps

from django.contrib.contenttypes.models import ContentType

from ecs.tasks.models import Task
from ecs.users.utils import sudo

def get_obj_tasks(activities, obj, data=None):
    tasks = Task.objects.filter(workflow_token__in=obj.workflow.tokens.filter(node__node_type__in=[a._meta.node_type for a in activities]).values('pk').query, deleted_at=None)
    if data:
        tasks = tasks.filter(workflow_token__node__data_id=data.pk, workflow_token__node__data_ct=ContentType.objects.get_for_model(type(data)))
    return tasks

def block_if_task_exists(node_uid):
    ''' For tasks which should only be started once '''
    def _decorator(func):
        @wraps(func)
        def _inner(wf):
            with sudo():
                task_exists = Task.objects.for_data(wf.data).filter(task_type__workflow_node__uid=node_uid).exists()
            if task_exists:
                return False
            else:
                return func(wf)
        return _inner
    return _decorator
