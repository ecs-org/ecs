from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django import forms
from django.template.defaultfilters import slugify
from django.utils import simplejson
from haystack.views import SearchView
from haystack.forms import HighlightedSearchForm
from haystack.query import SearchQuerySet
from haystack.utils import Highlighter

from ecs.documents.models import Page, Document


def download_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    # FIXME: get object via redirect to mediaserver
    response = HttpResponse(doc.file, content_type=doc.mimetype)
    ext = 'pdf'
    if 'excel' in doc.mimetype:
        ext = 'xls'
    response['Content-Disposition'] = 'attachment;filename=%s.%s' % (
        slugify("%s-%s-%s" % (doc.doctype and doc.doctype.name or 'Unterlage', doc.version, doc.date.strftime('%Y.%m.%d'))),
        ext,
    )
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
        highlighter = Highlighter(q, max_length=100)
        for result in qs:
            results.append({
                'page_number': result.page,
                'highlight': highlighter.highlight(result.text),
            })
    return HttpResponse(simplejson.dumps(results), content_type='text/plain')
    
