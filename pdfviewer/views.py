# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.documents.models import Document
from ecs.core.models import SubmissionForm

from ecs.pdfviewer.models import DocumentAnnotation
from ecs.pdfviewer.forms import DocumentAnnotationForm, AnnotationSharingForm
from ecs.utils.msutils import generate_docshot_urllist


def show(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    annotations = list(document.annotations.filter(user=request.user).values('pk', 'page_number', 'x', 'y', 'width', 'height', 'text', 'author__id', 'author__username'))

    return render(request, 'pdfviewer/viewer.html', {
        'document': document,
        'annotations': simplejson.dumps(annotations),
        'images': simplejson.dumps(generate_docshot_urllist(document.uuid_document, document.pages)),
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

def copy_annotations(request):
    submission_form_pk = request.GET.get('submission_form_pk', None)
    annotations = DocumentAnnotation.objects.filter(user=request.user).select_related('document').order_by('document', 'page_number', 'y')
    if submission_form_pk:
        sf = get_object_or_404(SubmissionForm, pk=submission_form_pk)
        annotations.filter(document__submission_forms=sf)
    return render(request, 'pdfviewer/annotations/copy.html', {
        'annotations': annotations,
    })
    
def share_annotations(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    annotations = DocumentAnnotation.objects.filter(user=request.user).order_by('page_number', 'y')
    form = AnnotationSharingForm(request.POST or None)
    
    if form.is_valid():
        user = form.cleaned_data['user']
        annotations = annotations.filter(pk__in=request.POST.getlist('annotation'))
        for annotation in annotations:
            annotation.pk = None
            annotation.user = user
            annotation.save()
        return render(request, 'pdfviewer/annotations/sharing/success.html', {
            'document': document,
            'target_user': user,
            'annotations': annotations,
        })
        
    return render(request, 'pdfviewer/annotations/sharing/share.html', {
        'document': document,
        'form': form,
        'annotations': annotations,
    })
    
    
    