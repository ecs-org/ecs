# -*- coding: utf-8 -*-
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
    annotations = dict([(anno.uuid, simplejson.loads(anno.layoutData)) for anno in Annotation.objects.filter(docid=id, page=page)])

    return render(request, 'pdfviewer/viewer.html', {
        'document': document,
        'annotations': simplejson.dumps(annotations),
        'images': simplejson.dumps(document_provider.createDocshotData(document.uuid_document)),
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