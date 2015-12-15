import logging

from celery.signals import task_failure, worker_process_init


logger = logging.getLogger('task')

def process_failure_signal(exception, traceback, sender, task_id, signal, args, kwargs, einfo, **kw):
    exc_info = (type(exception), exception, traceback)
    logger.error(
        unicode(exception),
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


def worker_startup(**kwargs):
    from ecs.integration.startup import startup
    startup()

worker_process_init.connect(worker_startup)
