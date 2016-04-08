from django import template

from ecs.tasks.models import Task
from ecs.users.utils import sudo
from ecs.core.diff import diff_submission_forms
from ecs.core.models import SubmissionForm

register = template.Library()

@register.filter
def amendment_reviewer(notification):
    reviewer = None
    with sudo():
        closed_tasks = Task.objects.for_data(notification.amendmentnotification).closed()
        try:
            task = closed_tasks.filter(task_type__workflow_node__uid__in=['notification_group_review', 'executive_amendment_review']).order_by('-created_at')[0]
            return task.assigned_to
        except IndexError:
            pass

@register.filter
def diff_from_docstash(docstash):
    extra = docstash['extra']
    old_submission_form = SubmissionForm.objects.get(id=extra['old_submission_form_id'])
    new_submission_form = SubmissionForm.objects.get(id=extra['new_submission_form_id'])
    return diff_submission_forms(old_submission_form, new_submission_form).html()

@register.filter
def diff(notification, plainhtml=False):
    return notification.get_diff(plainhtml=plainhtml)
