from django.http import Http404
from django.shortcuts import get_object_or_404

from ecs.docstash.models import DocStash
from ecs.documents.models import Document
from ecs.documents.views import handle_download


def download_document(request, docstash_key=None, document_pk=None, view=False):
    docstash = get_object_or_404(DocStash, key=docstash_key, owner=request.user)
    if int(document_pk) not in docstash.value['document_pks']:
        raise Http404()
    return handle_download(request, Document.objects.get(pk=document_pk), view=view)


def view_document(request, docstash_key=None, document_pk=None):
    return download_document(request, docstash_key, document_pk, view=True)
