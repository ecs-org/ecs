from urllib import urlencode

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.urlresolvers import reverse

from ecs.utils.viewutils import render
from ecs.documents.models import Document
from ecs.documents.forms import DocumentForm
from ecs.documents.signals import on_document_download


def upload_document(request, template='documents/upload_form.html'):
    form = DocumentForm(request.POST or None, request.FILES or None, prefix='document')
    documents = Document.objects.filter(pk__in=request.docstash.get('document_pks', []))
    if request.method == 'POST' and form.is_valid():
        new_document = form.save()
        documents |= Document.objects.filter(pk=new_document.pk)
        documents = documents.exclude(pk__in=documents.exclude(replaces_document=None).values('replaces_document').query)
        request.docstash['document_pks'] = [d.pk for d in documents]
        form = DocumentForm(prefix='document')
    return render(request, template, {
        'form': form,
        'documents': list(documents.order_by('doctype__identifier', 'version', 'date')),
    })

def delete_document(request, document_pk):
    document_pks = set(request.docstash.get('document_pks', []))
    if document_pk in document_pks:
        document_pks.remove(document_pk)
    request.docstash['document_pks'] = list(document_pks)
    

def handle_download(request, doc):
    url = doc.get_downloadurl()
    if url and doc.doctype.is_downloadable or request.user.ecs_profile.is_internal:
        on_document_download.send(Document, document=doc, user=request.user)
        return HttpResponseRedirect(url)
    else:
        return HttpResponseForbidden()


def view_document(request, document_pk=None, page=None):
    doc = get_object_or_404(Document, pk=document_pk)
    params = urlencode({
        'file': reverse(
            'ecs.documents.views.download_document',
            kwargs={'document_pk': doc.pk}
        )
    })
    url = '{}3rd-party/pdfjs/web/viewer.html?{}'.format(
        settings.MEDIA_URL, params)
    if page:
        url = '{}#page={}'.format(url, int(page))
    return HttpResponseRedirect(url)


def download_document(request, document_pk=None):
    # authorization is handled by ecs.authorization, see ecs.auth_conf for details.
    doc = get_object_or_404(Document, pk=document_pk)
    return handle_download(request, doc)
