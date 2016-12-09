import logging

from datetime import timedelta

from celery.signals import task_failure
from celery.task import periodic_task

from django.core.management import call_command

logger = logging.getLogger('task')

def process_failure_signal(exception, traceback, sender, task_id, signal, args, kwargs, einfo, **kw):
    exc_info = (type(exception), exception, traceback)
    logger.error(
        str(exception),
        exc_info=exc_info,
        extra={
            'data': {
                'task_id': task_id,
                'sender': sender,
                'args': args,
                'kwargs': kwargs,
            }
        }
    )
task_failure.connect(process_failure_signal)


@periodic_task(run_every=timedelta(days=1))
def clearsessions():
    call_command('clearsessions')
