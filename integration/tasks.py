import logging

from django.conf import settings

from celery.decorators import task, periodic_task
from celery.schedules import crontab
from celery.signals import task_failure
from sentry.client.handlers import SentryHandler

from ecs.mediaserver.diskbuckets import DiskBuckets, BucketError
from ecs.mediaserver.diskbuckets import ignore_all, ignore_none, onerror_log, satisfied_on_newer_then


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


@periodic_task(run_every=crontab(hour=3, minute=58))
def age_tempfile_dir(dry_run=False, **kwargs):
    ''' ages settings.TEMPFILE_DIR with files older than 14 days '''
    logger = age_tempfile_dir.get_logger(**kwargs)
    db = DiskBuckets(settings.TEMPFILE_DIR, max_size=0)
    ifunc = ignore_none if not dry_run else ignore_all
    
    logger.debug("start aging TEMPFILE_DIR {0}, TEMPFILE_DIR_MAXAGE {1}".format(
        settings.TEMPFILE_DIR, settings.TEMPFILE_DIR_MAXAGE))
    db.age(ignoreitem=ifunc, onerror=onerror_log,
        satisfied=satisfied_on_newer_then(settings.TEMPFILE_DIR_MAXAGE))
    logger.info("aging TEMPFILE_DIR was successful")
