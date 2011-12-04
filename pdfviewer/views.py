# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from ecs.utils.viewutils import render, redirect_to_next_url
from ecs.documents.models import Document
from ecs.core.models import SubmissionForm
from ecs.communication.utils import send_system_message_template
from ecs.utils.security import readonly

from ecs.pdfviewer.models import DocumentAnnotation
from ecs.pdfviewer.forms import DocumentAnnotationForm, AnnotationSharingForm


@readonly()
def show(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    annotations = list(document.annotations.filter(user=request.user).order_by('page_number', 'y').values('pk', 'page_number', 'x', 'y', 'width', 'height', 'text', 'author__id', 'author__username'))

    if request.method == 'POST':
        usersettings = request.user.ecs_settings

        settings = {'metaKey': request.POST['metaKey']}

        usersettings.pdfviewer_settings = settings
        usersettings.save()
    
    title_bits = []
    if hasattr(document.parent_object, 'submission'):
        title_bits.append(document.parent_object.submission.get_ec_number_display())
    title_bits += [u'%s:' % document.doctype_name, document.name]
    if document.parent_object:
        if isinstance(document.parent_object, SubmissionForm):
            parent = document.parent_object.project_title
        else:
            parent = unicode(document.parent_object)
        title_bits += [_(u' for '), parent]
    title_bits.append(u'(Version: %s)' % document.version)

    return render(request, 'pdfviewer/viewer.html', {
        'document': document,
        'title': u' '.join(title_bits),
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
        return HttpResponseBadRequest(_('invalid data: %s' % form.errors))

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
        annotations = annotations.filter(document__submission_forms=sf)
    return render(request, 'pdfviewer/annotations/copy.html', {
        'annotations': annotations,
    })

def share_annotations(request, document_pk=None):
    document = get_object_or_404(Document, pk=document_pk)
    annotations = document.annotations.filter(user=request.user).order_by('page_number', 'y')
    form = AnnotationSharingForm(request.POST or None)
    
    if form.is_valid():
        user = form.cleaned_data['user']
        annotations = annotations.filter(pk__in=request.POST.getlist('annotation'))
        for annotation in annotations:
            annotation.pk = None
            annotation.user = user
            annotation.save()
        message_params = {
            'user': request.user, 
            'url': request.build_absolute_uri(reverse('ecs.pdfviewer.views.show', kwargs={'document_pk': document_pk})),
        }
        send_system_message_template(user, _(u'%(user)s shared annotations with you.') % message_params, 'pdfviewer/annotations/sharing/shared.txt', message_params)
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
