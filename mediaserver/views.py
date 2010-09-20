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

#FIXME remove test code
def upload_pdf(request):
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['pdffile']
            docprovider.addBlob(MediaBlob(uuid4()), file.read())
            return HttpResponse("saved")
    else:
        form = PdfUploadForm(request.POST, request.FILES)

    return render_to_response('mediaserver/pdfupload.html', {'form': form})

def download_pdf(request, uuid):
    if not s3utils.verifyExpiringUrlString(request.get_full_path()):
        return HttpResponseBadRequest("Invalid expiring url");
    
    f = docprovider.getBlob(MediaBlob(UUID(uuid)))

    if f:
        return HttpResponse(f.read(), mimetype='application/pdf')
    else:
        return HttpResponseNotFound()
    
def list_docshots(request, uuid):
    tiles = [ 1, 3, 5 ]
    width = [ 800, 768 ] 
    links = [];

    doc = MediaBlob(UUID(uuid));
    for t in tiles:
        for w in width:
            pagenum = 1
            while docprovider.getDocshot(Docshot(doc, t, t, w , pagenum)):
                bucket = "/mediaserver/%s/%dx%d/%d/%d/" % (uuid, t, t, w, pagenum)
                expiringUrl = s3utils.createExpiringUrl("http://localhost:8000", bucket, '', "LocalFileStorageVault", int(time()) + 60)
                links.append(expiringUrl)
                pagenum += 1
    
    return HttpResponse(json.dumps(links), mimetype='text/javascript')
