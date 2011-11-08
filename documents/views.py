from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils import simplejson
from ecs.utils.viewutils import render

from haystack.views import SearchView
from haystack.forms import HighlightedSearchForm
from haystack.query import SearchQuerySet
from haystack.utils import Highlighter

from ecs.documents.models import Page, Document
from ecs.documents.forms import DocumentForm


HIGHLIGHT_PREFIX_WORD_COUNT = 3

class DocumentHighlighter(Highlighter):
    def find_window(self, highlight_locations):
        best_start, best_end = super(DocumentHighlighter, self).find_window(highlight_locations)
        return (max(0, best_start - 1 - len(' '.join(self.text_block[:best_start].rsplit(' ', HIGHLIGHT_PREFIX_WORD_COUNT + 1)[1:]))), best_end)

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
        return HttpResponseRedirect(url)
    else:
        return HttpResponseForbidden()


def download_document(request, document_pk=None):
    # authorization is handled by ecs.authorization, see ecs.auth_conf for details.
    doc = get_object_or_404(Document, pk=document_pk)
    return handle_download(request, doc)
        
def document_search_json(request, document_pk=None):
    q = request.GET.get('q', '')
    results = []
    if q:
        qs = SearchQuerySet().models(Page).order_by('doc_pk', 'page').filter(doc_pk=document_pk).auto_query(q)
        results = []
        highlighter = DocumentHighlighter(q, max_length=100)
        for result in qs:
            results.append({
                'page_number': result.page,
                'highlight': highlighter.highlight(result.text),
            })
    return HttpResponse(simplejson.dumps(results), content_type='text/plain')
    
