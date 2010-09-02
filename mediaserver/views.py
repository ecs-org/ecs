# -*- coding: utf-8 -*-

import email.utils
import time

from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings

from ecs.core.models import Document
from ecs.mediaserver.imageset import ImageSet
from ecs.mediaserver.renderer import Renderer
from ecs.mediaserver.storage import Cache, SetData
from ecs.utils import hashauth
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.docshot import Docshot
from ecs.mediaserver.forms.pdfuploadform import PdfUploadForm
from django.shortcuts import render_to_response
from ecs.mediaserver.document import PdfDocument

docprovider = DocumentProvider()

def docshot(request, uuid, tiles_x, tiles_y, zoom, pagenr):
    print '%s, %s, %s, %s, %s' % (uuid, tiles_x, tiles_y, zoom, pagenr)
    
    docshot = docprovider.fetch(Docshot(tiles_x, tiles_y, zoom, pagenr, uuid=uuid), volatile=True, disk=False, vault=False)
    
    return HttpResponse(docshot.__str__())
    
def upload_pdf(request):
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file=request.FILES['pdffile']
            doc = PdfDocument(data=file)
            docprovider.store(doc, use_vault=True)
            return HttpResponse("saved")
    else:
        form = PdfUploadForm(request.POST, request.FILES)
    return render_to_response('mediaserver/pdfupload.html', {'form': form})

def download_pdf(request, uuid):
    return HttpResponse(docprovider.fetch(PdfDocument(uuid=uuid), vault=True), mimetype='application/pdf')
