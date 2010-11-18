from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils import simplejson
from haystack.views import SearchView
from haystack.forms import HighlightedSearchForm
from haystack.query import SearchQuerySet
from haystack.utils import Highlighter

from ecs.documents.models import Page, Document, C_BRANDING_CHOICES
from ecs.utils.msutils import generate_media_url, generate_blob_url, generate_document_url 

HIGHLIGHT_PREFIX_WORD_COUNT = 3

class DocumentHighlighter(Highlighter):
    def find_window(self, highlight_locations):
        best_start, best_end = super(DocumentHighlighter, self).find_window(highlight_locations)
        return (max(0, best_start - 1 - len(' '.join(self.text_block[:best_start].rsplit(' ', HIGHLIGHT_PREFIX_WORD_COUNT + 1)[1:]))), best_end)


def download_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    filename = doc.get_filename()
    # fixme: authorization: is the user authorized to see dokument pk
    
    if (not doc.allow_download) or (doc.branding not in [c[0] for c in C_BRANDING_CHOICES]):
        return HttpResponseForbidden()
    
    if doc.mimetype != "application/pdf"or doc.branding == "n":
        response = HttpResponseRedirect(generate_blob_url(doc.uuid_document, filename, doc.mimetype))
    elif doc.branding == "b":
        response = HttpResponseRedirect(generate_document_url(doc.uuid_document, filename, None))
    elif doc.branding == "p":
        personalization = doc.add_personalization(request.user)
        branding = personalization.id
        response = HttpResponseRedirect(generate_document_url(doc.uuid_document, filename, branding))
    else:
        return HttpResponseForbidden()
    
    return response


class DocumentSearchView(SearchView):
    session_key = 'docsearch:q'

    def __call__(self, request, document_pk=None):
        self.document_pk = document_pk
        return super(DocumentSearchView, self).__call__(request)
        
    def get_query(self):
        q = super(DocumentSearchView, self).get_query()
        self.request.session[self.session_key] = q
        return q
        
    def build_form(self, form_kwargs=None): # mostly copied from haystack.forms
        data = None
        kwargs = {
            'load_all': self.load_all,
        }
        if form_kwargs:
            kwargs.update(form_kwargs)
        
        q = self.request.session.get(self.session_key, '')
        
        if len(self.request.GET):
            data = self.request.GET
            
        if q and not data:
            data = {'q': q}
        
        if self.searchqueryset is not None:
            kwargs['searchqueryset'] = self.searchqueryset
        
        return self.form_class(data, **kwargs)

    def get_results(self):
        results = super(DocumentSearchView, self).get_results()
        if self.document_pk:
            results = results.filter(doc_pk=self.document_pk)
        return results
        
    def extra_context(self):
        ctx = super(DocumentSearchView, self).extra_context()
        if self.document_pk:
            ctx['document'] = get_object_or_404(Document, pk=self.document_pk)
        return ctx

# haystack's search_view_factory does not pass *args and **kwargs
def search_view_factory(view_class=SearchView, *args, **kwargs):
    def search_view(request, *view_args, **view_kwargs):
        return view_class(*args, **kwargs)(request, *view_args, **view_kwargs)
    return search_view

document_search = search_view_factory(
    view_class=DocumentSearchView,
    template='documents/search.html',
    searchqueryset=SearchQuerySet().models(Page).order_by('doc_pk', 'page'), # '-doc_date', 'doc_type_name', '-doc_version',
    form_class=HighlightedSearchForm,
)

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
    
