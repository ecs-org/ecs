# -*- coding: utf-8 -*-
from django.conf import settings

from celery.decorators import task, periodic_task
from celery.schedules import crontab

from ecs.documents.models import Document
from ecs.documents.storagevault import getVault
from ecs.mediaserver.diskbuckets import DiskBuckets, ignore_all, ignore_none, onerror_log, satisfied_on_newer_then


@task()
def upload_to_storagevault(document_pk=None, **kwargs):
    logger = upload_to_storagevault.get_logger(**kwargs)
    logger.info('Uploading document with pk={0} to storagevault'.format(document_pk))
    result = False

    # atomic operation
    updated = Document.objects.filter(status='new', pk=document_pk).update(status='uploading')
    if not updated:
        logger.warning('Document with pk={0} and status=new does not exist'.format(document_pk))
        return result

    doc = Document.objects.get(pk=document_pk)
    
    try:
        getVault()[doc.uuid] = doc.file
    except Exception as e:
        if doc.retries < 5:
            doc.status = 'new'
            doc.retries += 1
        else:
            doc.status = 'aborted'
        
        logger.error("Can't upload document with uuid={0}. Retries was {1}, exception was {2}".format(
            doc.uuid, doc.retries, e))
    
    else:        
        doc.status = 'ready'
        doc.retries = 0
        result = True
    
    finally:
        doc.save()     
    
    return result
    
    
@periodic_task(run_every=crontab(hour=3, minute=48))
def age_incoming(dry_run=False, **kwargs):
    ''' ages settings.INCOMING_FILESTORE with files older than 14 days '''
    logger = age_incoming.get_logger(**kwargs)
    db = DiskBuckets(settings.INCOMING_FILESTORE, max_size=0)
    ifunc = ignore_none if not dry_run else ignore_all
    
    logger.debug("start aging INCOMING_FILESTORE {0}, INCOMING_FILESTORE_MAXAGE {1}".format(
        settings.INCOMING_FILESTORE, settings.INCOMING_FILESTORE_MAXAGE))
    db.age(ignoreitem=ifunc, onerror=onerror_log,
        satisfied=satisfied_on_newer_then(settings.INCOMING_FILESTORE_MAXAGE))
    logger.info("aging INCOMING_FILESTORE was successful")
