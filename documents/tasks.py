# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings

from celery.decorators import task, periodic_task
from celery.schedules import crontab

from haystack import site

from ecs.utils.pdfutils import pdf2text, pdf_page_count
from ecs.documents.models import Document, Page
from ecs.mediaserver.client import add_to_storagevault
from ecs.mediaserver.diskbuckets import DiskBuckets, ignore_all, ignore_none, onerror_log, satisfied_on_newer_then


@periodic_task(run_every=timedelta(seconds=10))
def document_tamer(**kwargs):
    logger = document_tamer.get_logger(**kwargs)

    to_be_indexed_documents = Document.objects.filter(status='new').values('pk')
    if len(to_be_indexed_documents):
        logger.info('{0} documents to be indexed'.format(len(to_be_indexed_documents)))
    for doc in to_be_indexed_documents:
        index_pdf.delay(doc['pk'])

    to_be_uploaded_documents = Document.objects.filter(status='indexed').values('pk')
    if len(to_be_uploaded_documents):
        logger.info('{0} documents to be uploaded'.format(len(to_be_uploaded_documents)))
    for doc in to_be_uploaded_documents:
        upload_to_storagevault.delay(doc['pk'])

    #filename = t.file.name
    #t.file = None
    #DocumentFileStorage().delete(filename)
    #t.save()        


@task()
def upload_to_storagevault(document_pk=None, **kwargs):
    logger = upload_to_storagevault.get_logger(**kwargs)
    logger.info('Uploading document with pk={0} to storagevault'.format(document_pk))
    result = False

    # atomic operation
    updated = Document.objects.filter(status='indexed', pk=document_pk).update(status='uploading')
    if not updated:
        logger.warning('Document with pk={0} and status=new does not exist'.format(document_pk))
        return result

    doc = Document.objects.get(pk=document_pk)
    
    try:
        add_to_storagevault(doc.uuid, doc.file)
    except Exception as e:
        if doc.retries < 5:
            doc.status = 'indexed'
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
    
    
@task()
def index_pdf(document_pk=None, **kwargs):
    logger = index_pdf.get_logger(**kwargs)
    logger.info('Indexing document with pk={0}'.format(document_pk))
    result = False

    # atomic operation
    updated = Document.objects.filter(status='new', pk=document_pk).update(status='indexing')
    if not updated:
        logger.warning('Document with pk={0} and status=new does not exist'.format(document_pk))
        return False

    doc = Document.objects.get(pk=document_pk)
    
    if doc.mimetype != 'application/pdf':
        result = True
        doc.status = 'indexed'
        doc.retries = 0
        doc.save()    
    
    else:
        try:
            doc.pages = pdf_page_count(doc.file) # calculate number of pages
    
            text_list = pdf2text(doc.file.path)
            assert len(text_list) == doc.pages
            for p, text in enumerate(text_list, 1):
                doc.page_set.create(num=p, text=text)
            
            index = site.get_index(Page)
            index.backend.update(index, doc.page_set.all())
            
        except Exception as e:
            if doc.retries < 3:
                doc.status = 'new'
                doc.retries += 1
            else:
                doc.status = 'aborted'
            
            logger.error("Can't index document with uuid={0}. Retries was {1}, exception was {2}".format(doc.uuid, doc.retries, e))
        
        else:        
            doc.status = 'indexed'
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
