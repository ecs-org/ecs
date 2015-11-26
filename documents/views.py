from urllib import urlencode

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.core.urlresolvers import reverse

from ecs.utils.viewutils import render
from ecs.documents.models import Document, DownloadHistory
from ecs.documents.forms import DocumentForm


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
    if (not doc.doctype.is_downloadable and
        not request.user.get_profile().is_internal):
        return HttpResponseForbidden()

    f = doc.get_from_mediaserver()

    response = HttpResponse(f)
    response['Content-Disposition'] = \
        'attachment;filename={}'.format(doc.get_filename())
    # XXX: set cache control http headers

    DownloadHistory.objects.create(document=doc, user=request.user)
    return response


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
