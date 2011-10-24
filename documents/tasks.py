# -*- coding: utf-8 -*-

import logging

from datetime import timedelta

from django.conf import settings
from django.utils.encoding import smart_str
from django.db.models import Q

from celery.decorators import task, periodic_task
from celery.schedules import crontab

from haystack import site

from ecs.utils.pdfutils import pdf2text, pdf_page_count
from ecs.documents.models import Document, Page

from ecs.mediaserver.client import prime_mediaserver, add_to_storagevault
from ecs.mediaserver.diskbuckets import DiskBuckets, BucketError, ignore_all, ignore_none, onerror_log, satisfied_on_newer_then


TO_BE_INDEXED = 'new' 
TO_BE_UPLOADED = 'indexed'
TO_BE_READY = 'uploaded'
TO_BE_INDEXED_Q = Q(status=TO_BE_INDEXED)
TO_BE_UPLOADED_Q = Q(status=TO_BE_UPLOADED)
TO_BE_READY_Q = Q(status=TO_BE_READY)


@periodic_task(run_every=timedelta(seconds=10))
def document_tamer(**kwargs):
    logger = document_tamer.get_logger(**kwargs)

    to_be_indexed_documents = Document.objects.filter(TO_BE_INDEXED_Q).values('pk')
    if len(to_be_indexed_documents):
        logger.info('{0} documents to be indexed'.format(len(to_be_indexed_documents)))
    for doc in to_be_indexed_documents:
        index_pdf.delay(doc['pk'])

    to_be_uploaded_documents = Document.objects.filter(TO_BE_UPLOADED_Q).values('pk')
    if len(to_be_uploaded_documents):
        logger.info('{0} documents to be uploaded'.format(len(to_be_uploaded_documents)))
    for doc in to_be_uploaded_documents:
        upload_to_storagevault.delay(doc['pk'])

    to_be_ready_documents = Document.objects.filter(TO_BE_READY_Q).values('pk')
    if len(to_be_ready_documents):
        logger.info('{0} documents to be primed and set to ready'.format(len(to_be_ready_documents)))
    for doc in to_be_ready_documents:
        do_prime_mediaserver.delay(doc['pk'])
        
    #filename = t.file.name
    #t.file = None
    #DocumentFileStorage().delete(filename)
    #t.save()        


@task()
def do_prime_mediaserver(document_pk=None, **kwargs):
    logger = do_prime_mediaserver.get_logger(**kwargs)
    logger.info('prime mediaserver with document pk={0}'.format(document_pk))
    result = False

    # atomic operation
    updated = Document.objects.filter(TO_BE_READY_Q, pk=document_pk).update(status='prime')
    if not updated:
        logger.warning('Document with pk={0} and status=uploaded does not exist'.format(document_pk))
        return result

    doc = Document.objects.get(pk=document_pk)
    doc.status = 'ready'
    doc.retries = 0
    try:
        success, response = prime_mediaserver(doc.uuid, doc.mimetype)
        if not success:
            logger.warning("Can't prime cache for document with uuid={0}. Response was {1}".format(doc.uuid, response))    
        else:
            logger.info('prime cachen for document with uuid={0} was successful'.format(doc.uuid))
    finally:
        doc.save()

    result = True


@task()
def upload_to_storagevault(document_pk=None, **kwargs):
    logger = upload_to_storagevault.get_logger(**kwargs)
    logger.info('Uploading document with pk={0} to storagevault'.format(document_pk))
    result = False

    # atomic operation
    updated = Document.objects.filter(TO_BE_UPLOADED_Q, pk=document_pk).update(status='uploading')
    if not updated:
        logger.warning('Document with pk={0} and status=new does not exist'.format(document_pk))
        return result

    doc = Document.objects.get(pk=document_pk)
    
    try:
        add_to_storagevault(doc.uuid, doc.file)
    except Exception as e:
        if doc.retries < 5:
            doc.status = TO_BE_UPLOADED
            doc.retries += 1
        else:
            doc.status = 'aborted'
        
        logger.error("Can't upload document with uuid={0}. Retries was {1}, exception was {2}".format(
            doc.uuid, doc.retries, e))
    
    else:        
        doc.status = TO_BE_READY
        doc.retries = 0
        result = True
    
    finally:
        doc.save()     
    
    return result
    
    
@task()
def index_pdf(document_pk=None, **kwargs):
    logger = index_pdf.get_logger(**kwargs)
    logger.info('Indexing document with pk={0}'.format(document_pk))
    result = False

    # atomic operation
    updated = Document.objects.filter(TO_BE_INDEXED_Q, pk=document_pk).update(status='indexing')
    if not updated:
        logger.warning('Document with pk={0} and status=uploaded does not exist'.format(document_pk))
        return False

    doc = Document.objects.get(pk=document_pk)
    
    if doc.mimetype != 'application/pdf':
        result = True
        doc.status = TO_BE_UPLOADED
        doc.retries = 0
        doc.save()    
    
    else:
        try:
            doc.pages = pdf_page_count(doc.file) # calculate number of pages
    
            for p in xrange(1, doc.pages + 1):
                text = pdf2text(doc.file.path, p)
                doc.page_set.create(num=p, text=text)
            
            index = site.get_index(Page)
            index.backend.update(index, doc.page_set.all())
            
        except Exception as e:
            if doc.retries < 3:
                doc.status = TO_BE_INDEXED
                doc.retries += 1
            else:
                doc.status = 'aborted'
            
            logger.error("Can't index uploaded document with uuid={0}. Retries was {1}, exception was {2}".format(doc.uuid, doc.retries, e))
        
        else:        
            doc.status = TO_BE_UPLOADED
            doc.retries = 0
            result = True
        
        finally:
            doc.save()     
    
    return result

    

#@periodic_task(track_started=True, run_every=crontab(hour=3, minute=48, day_of_week="*"))
@task()
def age_incoming(dry_run=False, **kwargs):
    ''' runs every night at 3:48, and ages settings.INCOMING_FILESTORE with files older than 14 days
    '''
    logger = logging.getLogger() #age_incoming.get_logger(**kwargs)
    db = DiskBuckets(settings.INCOMING_FILESTORE, max_size= 0)
    ifunc = ignore_none if not dry_run else ignore_all
    
    try:
        logger.debug("start aging INCOMING_FILESTORE {0}, INCOMING_FILESTORE_MAXAGE {1}".format(
            settings.INCOMING_FILESTORE, settings.INCOMING_FILESTORE_MAXAGE))
        db.age(ignoreitem= ifunc, onerror= onerror_log, 
            satisfied= satisfied_on_newer_then(settings.INCOMING_FILESTORE_MAXAGE))

    except BucketError as e:
        logger.warning("aging INCOMING_FILESTORE was not successful, until end of list reached; Exception Details {0}".format(e)) 
    
    else:
        logger.info("aging INCOMING_FILESTORE was successful")

