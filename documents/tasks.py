# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils.encoding import smart_str
from django.db.models import Q

from celery.decorators import task, periodic_task

from haystack import site

from ecs.utils.pdfutils import pdf2text, pdf_page_count

from ecs.mediaserver.client import prime_mediaserver, add_to_storagevault

from ecs.documents.models import Document, Page


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
        Document.objects.filter(pk= doc['pk']).update(status='ready')
        t = Document.objects.get(pk = doc['pk'])
        success, response = prime_mediaserver(t.uuid_document, t.mimetype)
        if not success:
            logger.warning("Can't prime cache for document with uuid={0}. Response was {1}".format(doc.uuid_document, response))    

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
    updated = Document.objects.filter(TO_BE_UPLOADED_Q, pk=document_pk).update(status='uploading')
    if not updated:
        logger.warning('Document with pk={0} and status=new does not exist'.format(document_pk))
        return result

    doc = Document.objects.get(pk=document_pk)
    
    try:
        add_to_storagevault(doc.uuid_document, doc.file)
    except Exception as e:
        if doc.retries < 5:
            doc.status = TO_BE_UPLOADED
            doc.retries += 1
        else:
            doc.status = 'aborted'
        
        logger.error("Can't upload document with uuid={0}. Retries was {1}, exception was {2}".format(
            doc.uuid_document, doc.retries, e))
    
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
            
            logger.error("Can't index uploaded document with uuid={0}. Retries was {1}, exception was {2}".format(doc.uuid_document, doc.retries, e))
        
        else:        
            doc.status = TO_BE_UPLOADED
            doc.retries = 0
            result = True
        
        finally:
            doc.save()     
    
    return result

    


def clean_older_than(dry_run=False, **kwargs):
    ''' runs every night at 3:38, and ages render_diskcache and doc_diskcache
    '''
    logger = logging.getLogger() #do_aging.get_logger(**kwargs)
    
    render_diskcache = DiskBuckets(settings.MS_SERVER ["render_diskcache"],
        max_size= settings.MS_SERVER ["render_diskcache_maxsize"])
    doc_diskcache = DiskBuckets(settings.MS_SERVER ["doc_diskcache"],
        max_size = settings.MS_SERVER ["doc_diskcache_maxsize"])

    ifunc = ignorefunc if not dry_run else dryrun_ignorefunc
    efunc = errorfunc
    
    try:
        logger.debug("start aging render_diskcache")    
        afunc = abortfuncgetter(settings.MS_SERVER ["render_diskcache_maxsize"])
        render_diskcache.age(ignorefunc= ifunc, errorfunc= efunc, abortfunc= afunc)
    except BucketError as e:
        logger.warning("aging render_diskcache was not successful, until end of list reached; Exception Details {0}".format(e)) 
    else:
        logger.info("aging render_diskcache was successful")

    try:
        logger.debug("start aging doc_diskcache") 
        afunc = abortfuncgetter(settings.MS_SERVER ["doc_diskcache_maxsize"])   
        doc_diskcache.age(ignorefunc= ifunc, errorfunc= efunc, abortfunc= afunc)
    except BucketError as e:
        logger.warning("aging doc_diskcache was not successful, until end of list reached; Exception Details {0}".format(e)) 
    else:
        logger.info("aging doc_diskcache was successful")


def abortfuncgetter(max_size):
    saved_max_size = max_size
    def abortfunc(current_size, filename, filesize, accesstime):
        #print("max size {0}, current size {1}, filesize {2}, accesstime {3}, filename {4}".format(
        #    saved_max_size, current_size, filesize, time.ctime(accesstime), filename))
        saved_current_size = current_size
        return current_size < saved_max_size
    return abortfunc

def dryrun_ignorefunc(filename, filesize, accesstime):
    logger = logging.getLogger() #do_aging.get_logger(**kwargs)
    logger.debug("dry_run: would remove file (date= {0}): {1}".format(time.ctime(accesstime), filename))
    return True

def ignorefunc(filename, filesize, accesstime):
    logger = logging.getLogger() #do_aging.get_logger(**kwargs)
    logger.debug("remove file (date= {0}): {1}".format(time.ctime(accesstime), filename))
    return False

def errorfunc(filename, filesize, accesstime, exception):
    logger = logging.getLogger() #do_aging.get_logger(**kwargs)
    logger.info("removing of file %s failed. Exception was: %s" % (filename, exception))
