# -*- coding: utf-8 -*-

import email.utils
import time

from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings

from ecs.core.models import Document
from ecs.mediaserver.imageset import ImageSet
from ecs.mediaserver.storage import Cache, SetData
from ecs.utils import hashauth
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.docshot import Docshot
from ecs.mediaserver.forms.pdfuploadform import PdfUploadForm
from django.shortcuts import render_to_response
from ecs.mediaserver.document import PdfDocument

docprovider = DocumentProvider()

def docshot(request, uuid, tiles_x, tiles_y, width, pagenr):
    print 'docshot request: %s, %s, %s, %s, %s' % (uuid, tiles_x, tiles_y, width, pagenr)
    
    docshot = Docshot(tiles_x, tiles_y, width, pagenr, uuid=uuid)
    f = docprovider.fetch(docshot, try_render_diskcache=True)
     
    return HttpResponse(f.read(), mimetype='image/png')
   
def upload_pdf(request):
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file=request.FILES['pdffile']
            doc = PdfDocument(data=file.read())
            docprovider.store(doc, use_vault=True)
            return HttpResponse("saved")
    else:
        form = PdfUploadForm(request.POST, request.FILES)
    return render_to_response('mediaserver/pdfupload.html', {'form': form})

def download_pdf(request, uuid):
    doc = PdfDocument(uuid=uuid)
    f = docprovider.fetch(doc, try_doc_diskcache=True)
    print "f", f
    return HttpResponse(f.read(), mimetype='application/pdf')
