# -*- coding: utf-8 -*-
import tempfile, shutil, logging

from django.conf import settings
from django.core.cache import cache

from celery.decorators import task, periodic_task
from celery.schedules import crontab

from ecs.mediaserver.diskbuckets import DiskBuckets, BucketError
from ecs.mediaserver.diskbuckets import ignore_all, ignore_none, onerror_log, satisfied_on_less_then


LOCK_EXPIRE = 60 * 10 # rendering lock expires in 10 minutes


@task(track_started=True)
def do_rendering(identifier=None, mimetype='application/pdf', **kwargs):
    ''' loads blob, rerender pages (if application/pdf) with expiring lock support.
    :return: if something fails (no identifier, ioError, lock-in-progress): false, str(identifier), type-of-fail-description
    :return: true, str(identifier), "" if successfull
    '''
    logger = do_rendering.get_logger(**kwargs)
    logger.debug("do_rendering called with identifier %s , mimetype %s" % (identifier, mimetype))
    
    if identifier is None:
        logger.warning("Warning, do_rendering (identifier is None)")
        return False, str(None), "identifier is none"

    from ecs.mediaserver.utils import MediaProvider
    mediaprovider = MediaProvider()
    
    lock_id = "%s-lock-render" % (identifier)
    # cache.add fails if if the key already exists
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    # memcache delete is very slow, but we have to use it to take advantage of using add() for atomic locking
    release_lock = lambda: cache.delete(lock_id)

    if acquire_lock():
        try:
            logger.debug("Lock %s acquired" % (lock_id))

            try:
                filelike = mediaprovider.get_blob(identifier)
            except KeyError as exceptobj:
                return False, '', repr(exceptobj)
            
            if mimetype!='application/pdf':
                result = True, str(identifier), ""
            else:
                try:    
                    render_dirname = tempfile.mkdtemp(dir= settings.TEMPFILE_DIR)
                    
                    for page, data in mediaprovider._render_pages(identifier, filelike, render_dirname):
                        mediaprovider.set_page(page, data, use_render_diskcache=True)
                        if hasattr(data, "close"):
                            data.close()
                except IOError as exceptobj:
                    result = False, str(identifier), repr(exceptobj)
                else:
                    result = True, str(identifier), ""
                finally:    
                    shutil.rmtree(render_dirname)        
        finally:
            release_lock()
        
        logger.debug("Lock %s released" % (lock_id))
        return result
    else:
        logger.info("rendering already in progress: do_rendering identifier %s , mimetype %s " % (identifier, mimetype))
        return False, str(identifier), "already in progress"
    
    

#@periodic_task(track_started=True, run_every=crontab(hour=3, minute=38, day_of_week="*"))
@task(track_started=True)
def do_aging(dry_run=False, **kwargs):
    ''' runs every night at 3:38, and ages render_diskcache and doc_diskcache
    '''
    logger = logging.getLogger() #do_aging.get_logger(**kwargs)
    
    render_diskcache = DiskBuckets(settings.MS_SERVER ["render_diskcache"],
        max_size= settings.MS_SERVER ["render_diskcache_maxsize"])
    doc_diskcache = DiskBuckets(settings.MS_SERVER ["doc_diskcache"],
        max_size = settings.MS_SERVER ["doc_diskcache_maxsize"])

    ifunc = ignore_none if not dry_run else ignore_all
    
    try:
        logger.debug("start aging render_diskcache")    
        sfunc = satisfied_on_less_then(settings.MS_SERVER ["render_diskcache_maxsize"])
        render_diskcache.age(ignoreitem= ifunc, onerror= onerror_log, satisfied= sfunc)
    
    except BucketError as e:
        logger.warning("aging render_diskcache was not successful, until end of list reached; Exception Details {0}".format(e)) 
    
    else:
        logger.info("aging render_diskcache was successful")

    try:
        logger.debug("start aging doc_diskcache") 
        sfunc = satisfied_on_less_then(settings.MS_SERVER ["doc_diskcache_maxsize"])   
        doc_diskcache.age(ignoreitem= ifunc, onerror= onerror_log, satisfied= sfunc)
    
    except BucketError as e:
        logger.warning("aging doc_diskcache was not successful, until end of list reached; Exception Details {0}".format(e)) 
    
    else:
        logger.info("aging doc_diskcache was successful")

