# -*- coding: utf-8 -*-

import os, tempfile

from django.conf import settings
from django.utils.encoding import smart_str
from celery.decorators import task
from haystack import site

from ecs.utils.pdfutils import pdf2text, pdf2pdfa
from ecs.utils.storagevault import getVault
from ecs.utils import gpgutils

from ecs.documents.models import Document, Page, DocumentFileStorage

@task()
def encrypt_and_upload_to_storagevault(document_pk=None, **kwargs):
    logger = encrypt_and_upload_to_storagevault.get_logger(**kwargs)
    try:
        doc = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.warning("Warning, Document with pk %s does not exist" % str(document_pk))
        return False
    
    vault = getVault() 
    encrypted, encrypted_name = tempfile.mkstemp()
    os.close(encrypted)
    encrypted = None
    #logger.debug("original path %s, uuid %s, encrypted name %s" % (str(doc.file.path), str(doc.uuid_document), encrypted_name))
    
    try:
        try:
            gpgutils.encrypt_sign(doc.file.path, encrypted_name,
                settings.STORAGE_ENCRYPT['gpghome'], settings.STORAGE_ENCRYPT["owner"])
        except IOError as e:
            logger.error("Error, can't encrypt document stored at %s with uuid %s as %r. Exception was %r"  % (doc.file.path, doc.uuid_document, encrypted_name, e))
        else:
            try:
                encrypted = open(encrypted_name, "rb")
                vault.add(doc.uuid_document, encrypted)
            except KeyError as e:
                logger.error("Error, can't upload uuid %s from %s to storage vault. Exception was %r " % (doc.uuid_document, encrypted_name, e))
    finally:
        if hasattr(encrypted, "close"):
            encrypted.close()
        if os.path.isfile(encrypted_name):
            os.remove(encrypted_name)
            
    # FIXME: prime mediaserver (depends on resolution of #713) 
    if doc.pages and doc.mimetype == 'application/pdf':    
        extract_and_index_pdf_text.apply_async(args=[doc.pk])
        
    return True
    
@task()
def extract_and_index_pdf_text(document_pk=None, **kwargs):
    logger = extract_and_index_pdf_text.get_logger(**kwargs)
    try:
        doc = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.warning("Warning, Document with pk %s does not exist" % str(document_pk))
        return False

    if not doc.pages or doc.mimetype != 'application/pdf':
        logger.info("Warning, doc.pages (%s) not set or doc.mimetype (%s) != 'application/pdf'" % (str(doc.pages), str(doc.mimetype)))
        return False

    #logger.debug("filename path %s %s" % (str(doc.file.path), str(doc.file.name)))
    for p in xrange(1, doc.pages + 1):
        text = pdf2text(doc.file.path, p)
        doc.page_set.create(num=p, text=text)

    index = site.get_index(Page)
    index.backend.update(index, doc.page_set.all())

    #DocumentFileStorage().delete(doc.file.name)

    return True
