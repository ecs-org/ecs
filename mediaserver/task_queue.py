# -*- coding: utf-8 -*-

import os, tempfile

from django.conf import settings
from celery.decorators import task
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.renderer import renderDefaultDocshots

@task()
def rerender_docshots(pdfblob=None, **kwargs):
    logger = rerender_docshots.get_logger(**kwargs)
    logger.debug("called with pdfblob %s" % pdfblob)
    
    if pdfblob is None:
        logger.warning("Warning, pdfblob is None")
        return False
    
    docprovider = DocumentProvider()
    filelike = docprovider.doc_diskcache.get(pdfblob.cacheID());
    
    for docshot, data in renderDefaultDocshots(pdfblob, filelike):
        docprovider.addDocshot(docshot, data, use_render_diskcache=True)
        
    return True