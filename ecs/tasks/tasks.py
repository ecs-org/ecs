from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models.expressions import RawSQL

from celery.task import periodic_task
from celery.schedules import crontab

from ecs.communication.utils import send_message
from ecs.tasks.models import Task
from ecs.users.utils import get_user


def _get_submission(task):
    if task.content_type.natural_key() == ('core', 'submission'):
        return task.data
    elif task.content_type.natural_key() == ('checklists', 'checklist'):
        return task.data.submission
    print(task.content_type.natural_key())
    assert False


def send_close_message(task):
    submission = _get_submission(task)
    subject = _('{task} completed').format(task=task.task_type)
    text = _('{user} has completed the {task}.').format(user=task.assigned_to,
        task=task.task_type)

    send_message(get_user('root@system.local'), task.created_by, subject, text,
        submission=submission)


@periodic_task(run_every=crontab(minute=0))
def send_reminder_messages():
    now = timezone.now()
    tasks = (Task.objects
        .filter(reminder_message_sent_at=None,
            reminder_message_timeout__isnull=False)
        .annotate(deadline=RawSQL('created_at + reminder_message_timeout', ()))
        .filter(deadline__lt=now))

    for task in tasks:
        submission = _get_submission(task)
        subject = _('{task} still open').format(task=task.task_type)
        text = _('{user} did not complete the {task} yet.').format(
            user=task.assigned_to, task=task.task_type)

        send_message(get_user('root@system.local'), task.created_by, subject,
            text, submission=submission)

        task.reminder_message_sent_at = now
        task.save()
