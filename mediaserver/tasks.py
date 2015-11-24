# -*- coding: utf-8 -*-
from django.conf import settings

from celery.decorators import periodic_task
from celery.schedules import crontab

from ecs.mediaserver.diskbuckets import DiskBuckets
from ecs.mediaserver.diskbuckets import ignore_all, ignore_none, onerror_log, satisfied_on_less_then

    
@periodic_task(run_every=crontab(hour=3, minute=38))
def do_aging(dry_run=False, **kwargs):
    ''' ages doc_diskcache '''
    logger = do_aging.get_logger(**kwargs)
    
    doc_diskcache = DiskBuckets(settings.MS_SERVER["doc_diskcache"],
        max_size=settings.MS_SERVER["doc_diskcache_maxsize"])

    ifunc = ignore_none if not dry_run else ignore_all

    logger.debug("start aging doc_diskcache") 
    sfunc = satisfied_on_less_then(settings.MS_SERVER["doc_diskcache_maxsize"])
    doc_diskcache.age(ignoreitem=ifunc, onerror=onerror_log, satisfied=sfunc)
    logger.info("aging doc_diskcache was successful")
