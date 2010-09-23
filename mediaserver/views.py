# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseBadRequest

from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.forms.pdfuploadform import PdfUploadForm
from django.shortcuts import render_to_response
from ecs.mediaserver.cacheobjects import MediaBlob, Docshot
from uuid import uuid4, UUID
from ecs.utils import s3utils
from time import time
import json

docprovider = DocumentProvider()

def docshot(request, uuid, tiles_x, tiles_y, width, pagenr):
    if not s3utils.verifyExpiringUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");
    
    f = docprovider.getDocshot(Docshot(MediaBlob(UUID(uuid)), tiles_x, tiles_y, width, pagenr))

    if f:
        return HttpResponse(f.read(), mimetype='image/png')
    else:
        return HttpResponseNotFound()

def download_pdf(request, uuid):
    if not s3utils.verifyExpiringUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");
    
    f = docprovider.getBlob(MediaBlob(UUID(uuid)))

    if f:
        return HttpResponse(f.read(), mimetype='application/pdf')
    else:
        return HttpResponseNotFound()
    
