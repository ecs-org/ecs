from django import template

from ecs.tasks.models import Task
from ecs.users.utils import sudo

register = template.Library()

@register.filter
def amendment_reviewer(notification):
    reviewer = None
    with sudo():
        closed_tasks = Task.objects.for_data(notification.amendmentnotification).filter(deleted_at__isnull=True, assigned_at__isnull=False, closed_at__isnull=False)
        try:
            task = closed_tasks.filter(task_type__workflow_node__uid__in=['notification_group_review', 'executive_amendment_review']).order_by('-created_at')[0]
            return task.assigned_to
        except IndexError:
            pass
