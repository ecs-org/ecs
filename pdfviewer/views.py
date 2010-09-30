# -*- coding: utf-8 -*-
import uuid
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.utils import simplejson
from django.shortcuts import get_object_or_404

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.documents.models import Document
from ecs.pdfviewer.models import Annotation
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.cacheobjects import MediaBlob

document_provider = DocumentProvider()

def show(request, id='1', page=1, zoom='1'):
    document = get_object_or_404(Document, pk=id)
    annotations = dict([(anno.uuid, JSONDecoder().decode(anno.layoutData)) for anno in Annotation.objects.filter(docid=id, page=page)])
    docdict = document_provider.createDocshotDictionary(MediaBlob(uuid.UUID(document.uuid_document)))

    return render(request, 'pdfviewer/viewer.html', {
        'document': document,
        'allAnno': simplejson.dumps(annotations),
        'images': simplejson.dumps(docdict),
    })


def demo(request):
    return render(request, 'pdfviewer/demo.html', {})

def annotation(request, did, page, zoom):
    if not request.POST:
        return HttpResponse('POST only')
        
    print did, page, zoom, request.POST
    anno = Annotation(uuid=request.POST['uuid'])
    anno.layoutData = request.POST['layoutData']
    anno.docid = Document.objects.get(id=did);
    anno.page = page;
    anno.save()
    return HttpResponse('OK')

def delete_annotation(request, did, page, zoom):
    if not request.POST:
        return HttpResponse('POST only')
        
    print did, page, zoom, request.POST
    anno = Annotation.objects.filter(uuid=request.POST['uuid']).delete()
    return HttpResponse('OK')