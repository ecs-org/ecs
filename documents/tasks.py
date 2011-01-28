# -*- coding: utf-8 -*-

import os, tempfile
from datetime import timedelta
from time import time
from urllib2 import urlopen

from django.conf import settings
from django.utils.encoding import smart_str
from django.db.models import Q
from celery.decorators import task, periodic_task
from haystack import site

from ecs.utils.pdfutils import pdf2text, pdf2pdfa
from ecs.utils.storagevault import getVault
from ecs.utils import gpgutils

from ecs.documents.models import Document, Page, DocumentFileStorage
from ecs.utils.pdfutils import pdf_page_count
from ecs.utils import s3utils

@periodic_task(run_every=timedelta(seconds=10))
def document_tamer(**kwargs):
    logger = document_tamer.get_logger(**kwargs)

    new_documents = Document.objects.filter(status='new').values('pk')
    if len(new_documents):
        logger.info('{0} new documents'.format(len(new_documents)))
    for doc in new_documents:
        upload_to_storagevault.delay(doc['pk'])

    uploaded_documents = Document.objects.filter(status='uploaded', mimetype='application/pdf').values('pk')
    if len(uploaded_documents):
        logger.info('{0} uploaded documents'.format(len(uploaded_documents)))
    for doc in uploaded_documents:
        index_pdf.delay(doc['pk'])

    indexed_documents = Document.objects.filter(Q(status='indexed', mimetype='application/pdf')|(Q(status='uploaded') | ~Q(mimetype='application/pdf')))
    updated = indexed_documents.update(status='ready')
    if updated:
        logger.info('{0} documents are now ready'.format(updated))


@task()
def upload_to_storagevault(document_pk=None, **kwargs):
    logger = upload_to_storagevault.get_logger(**kwargs)
    logger.info('Uploading document with pk={0} to storagevault'.format(document_pk))

    # atomic operation
    updated = Document.objects.filter(pk=document_pk, status='new').update(status='uploading')
    if not updated:
        logger.warning('Document with pk={0} and status=new does not exist'.format(document_pk))
        return False

    doc = Document.objects.get(pk=document_pk)
    
    try:
        with tempfile.NamedTemporaryFile() as tmp:
            try:
                gpgutils.encrypt_sign(doc.file.path, tmp.name, settings.STORAGE_ENCRYPT['gpghome'], settings.STORAGE_ENCRYPT['owner'])
            except IOError as e:
                logger.error("Can't encrypt document with pk={0}. Exception was {1}".format(document_pk, e))
                return False
            else:
                try:
                    getVault().add(doc.uuid_document, tmp)
                except KeyError as e:
                    logger.error("Can't upload document with uuid={0}. Exception was {1}".format(doc.uuid_document, e))
                    return False

        key_id = settings.MS_CLIENT['key_id']
        s3url = s3utils.S3url(key_id, settings.MS_CLIENT['key_secret'])

        objid_parts = ['prime', doc.uuid_document]
        objid = '/'.join(objid_parts) + '/'
        expires = int(time()) + settings.MS_SHARED['url_expiration_sec']
        url = s3url.createUrl(settings.MS_CLIENT['server'], settings.MS_CLIENT['bucket'], objid, key_id, expires)

        f = urlopen(url)
        response = f.read()
        if not response == 'ok':
            logger.error("Can't prime cache for document with uuid={0}. Response was {1}".format(doc.uuid_document, response))
            return False
        f.close()

    except Exception as e:
        doc.status = 'aborted'
        doc.save()
        logger.error("Can't upload document with uuid={0}. Exception was {1}".format(doc.uuid_document, e))
        return False
    else:
        doc.status = 'uploaded'
        doc.save()
        
    return True
    
@task()
def index_pdf(document_pk=None, **kwargs):
    logger = index_pdf.get_logger(**kwargs)
    logger.info('Indexing document with pk={0}'.format(document_pk))

    # atomic operation
    updated = Document.objects.filter(pk=document_pk, status='uploaded').update(status='indexing')
    if not updated:
        logger.warning('Document with pk={0} and status=uploaded does not exist'.format(document_pk))
        return False

    doc = Document.objects.get(pk=document_pk)
    
    try:
        doc.pages = pdf_page_count(doc.file) # calculate number of pages

        for p in xrange(1, doc.pages + 1):
            text = pdf2text(doc.file.path, p)
            doc.page_set.create(num=p, text=text)

        index = site.get_index(Page)
        index.backend.update(index, doc.page_set.all())

        #DocumentFileStorage().delete(doc.file.name)

    except Exception as e:
        doc.status = 'aborted'
        doc.save()
        logger.error("Can't upload document with uuid={0}. Exception was {1}".format(doc.uuid_document, e))
        return False
    else:
        doc.status = 'indexed'
        doc.save()
        
    return True

    