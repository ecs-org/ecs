from urllib.parse import urlencode, quote
from uuid import uuid4

from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from ecs.documents.models import Document
from ecs.documents.forms import DocumentForm


def upload_document(request, template='documents/upload_form.html'):
    form = DocumentForm(request.POST or None, request.FILES or None, prefix='document')
    documents = Document.objects.filter(pk__in=request.docstash.get('document_pks', []))
    if request.method == 'POST' and form.is_valid():
        new_document = form.save()
        documents |= Document.objects.filter(pk=new_document.pk)
        documents = documents.exclude(pk__in=documents.exclude(replaces_document=None).values('replaces_document').query)
        request.docstash['document_pks'] = [d.pk for d in documents]
        request.docstash.save()
        form = DocumentForm(prefix='document')
    return render(request, template, {
        'form': form,
        'documents': documents.order_by('doctype__identifier', 'date', 'name'),
    })

def delete_document(request, document_pk):
    document_pks = set(request.docstash.get('document_pks', []))
    if document_pk in document_pks:
        document_pks.remove(document_pk)
    request.docstash['document_pks'] = list(document_pks)
    request.docstash.save()


def handle_download(request, doc, view=False):
    if view:
        return handle_view(request, doc)

    if (not doc.doctype.is_downloadable and
        not request.user.profile.is_internal):
        raise PermissionDenied()

    response = FileResponse(doc.retrieve(request.user, 'download'),
        content_type=doc.mimetype)
    response['Content-Disposition'] = \
        'attachment;filename={}'.format(doc.get_filename())
    return response


def handle_view(request, doc):
    ref_key = uuid4().hex
    cache.set('document-ref-{}'.format(ref_key), doc.id, timeout=60)

    title_bits = [str(doc.doctype), doc.name]
    sf = doc.submission_forms.first()
    if sf:
        title_bits.insert(0, sf.submission.get_ec_number_display())
    n = doc.notifications.first()
    if n:
        title_bits.insert(0, str(n))

    version = '{} vom {}'.format(doc.version,
        timezone.localtime(doc.date).strftime('%d.%m.%Y'))
    if request.user.profile.is_internal:
        title_bits.insert(0, version)
    else:
        title_bits.append(version)

    params = urlencode({
        'file': reverse(
            'ecs.documents.views.download_once',
            kwargs={'ref_key': ref_key}
        ),
        'title': ' - '.join(title_bits),
    }, quote_via=quote)
    url = '{}3rd-party/pdfjs-1.5.188/web/viewer.html?{}'.format(
        settings.STATIC_URL, params)
    return redirect(url)


def download_once(request, ref_key=None):
    cache_key = 'document-ref-{}'.format(ref_key)
    doc_id = cache.get(cache_key)

    if not doc_id:
        raise Http404()

    cache.delete(cache_key)

    doc = get_object_or_404(Document, pk=doc_id)
    response = FileResponse(doc.retrieve(request.user, 'view'),
        content_type=doc.mimetype)

    # Disable browser caching, so the PDF won't end up on the users hard disk.
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Vary'] = '*'
    return response
