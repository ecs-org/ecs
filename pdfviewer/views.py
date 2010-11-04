# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.documents.models import Document

from ecs.pdfviewer.models import DocumentAnnotation
from ecs.pdfviewer.forms import DocumentAnnotationForm
from ecs.pdfviewer.utils import createmediaurls


def show(request, id='1', page=1, zoom='1'):
    document = get_object_or_404(Document, pk=id)
    annotations = list(document.annotations.filter(user=request.user).values('pk', 'page_number', 'x', 'y', 'width', 'height', 'text'))

    return render(request, 'pdfviewer/viewer.html', {
        'document': document,
        'annotations': simplejson.dumps(annotations),
        'images': simplejson.dumps(createmediaurls(document)),
    })

@csrf_exempt
def edit_annotation(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    try:
        annotation = DocumentAnnotation.objects.get(user=request.user, pk=request.POST.get('pk'))
    except DocumentAnnotation.DoesNotExist:
        annotation = None
    form = DocumentAnnotationForm(request.POST or None, instance=annotation, document=document)
    if form.is_valid():
        annotation = form.save(commit=False)
        annotation.document = document
        annotation.user = request.user
        annotation.author = request.user
        annotation.save()
        return HttpResponse('OK')
    else:
        return HttpResponseBadRequest('invalid data: %s' % form.errors)

@csrf_exempt
def delete_annotation(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    annotation = get_object_or_404(DocumentAnnotation, user=request.user, pk=request.POST.get('pk'))
    annotation.delete()
    return HttpResponse('OK')

def my_annotations(request, submission_form_pk=None):
    sf = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    
    return render(request, 'pdfviewer/annotations/list.html', {
        'annotations': DocumentAnnotation.objects.filter(user=request.user).filter(document__submission_forms=sf).order_by('page_number', 'y'),
    })