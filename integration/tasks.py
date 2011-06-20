import logging

from django.conf import settings

from celery.decorators import task, periodic_task
from celery.schedules import crontab

from ecs.mediaserver.diskbuckets import DiskBuckets, BucketError
from ecs.mediaserver.diskbuckets import ignore_all, ignore_none, onerror_log, satisfied_on_newer_then


@task()
#@periodic_task(track_started=True, run_every=crontab(hour=3, minute=58, day_of_week="*"))
def age_tempfile_dir(dry_run=False, **kwargs):
    ''' runs every night at 3:58, and ages settings.TEMPFILE_DIR with files older than 14 days
    '''
    logger = logging.getLogger() #age_tempfile_dir.get_logger(**kwargs)
    db = DiskBuckets(settings.TEMPFILE_DIR, max_size= 0)
    ifunc = ignore_none if not dry_run else ignore_all
    
    try:
        logger.debug("start aging TEMPFILE_DIR {0}, TEMPFILE_DIR_MAXAGE {1}".format(
            settings.TEMPFILE_DIR, settings.TEMPFILE_DIR_MAXAGE))    
        db.age(ignoreitem= ifunc, onerror= onerror_log, 
            satisfied= satisfied_on_newer_then(settings.TEMPFILE_DIR_MAXAGE))

    except BucketError as e:
        logger.warning("aging TEMPFILE_DIR was not successful, until end of list reached; Exception Details {0}".format(e)) 
    
    else:
        logger.info("aging TEMPFILE_DIR was successful")
