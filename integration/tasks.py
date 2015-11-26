import logging
import subprocess

from django.conf import settings

from celery.decorators import periodic_task
from celery.schedules import crontab
from celery.signals import task_failure, worker_process_init
from sentry.client.handlers import SentryHandler


logger = logging.getLogger('task')
logger.addHandler(SentryHandler())

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


@periodic_task(run_every=crontab(hour=3, minute=58))
def age_tempfile_dir(dry_run=False, **kwargs):
    ''' ages settings.TEMPFILE_DIR with files older than 14 days '''
    logger = age_tempfile_dir.get_logger(**kwargs)
    logger.debug("start aging TEMPFILE_DIR {0}, TEMPFILE_DIR_MAXAGE {1}".format(
        settings.TEMPFILE_DIR, settings.TEMPFILE_DIR_MAXAGE))

    subprocess.check_call([
        'find', settings.TEMPFILE_DIR,
        '-mtime', '+{}'.format(settings.TEMPFILE_DIR_MAXAGE),
        '-delete']
    )

    logger.info("aging TEMPFILE_DIR was successful")
