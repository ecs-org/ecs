from django.shortcuts import get_object_or_404
from haystack.views import SearchView
from haystack.forms import HighlightedSearchForm
from haystack.query import SearchQuerySet

from ecs.core.models import Page, Document

class DocumentSearchView(SearchView):
    def __call__(self, request, document_pk=None):
        self.document_pk = document_pk
        return super(DocumentSearchView, self).__call__(request)

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
    template='search/search.html',
    searchqueryset=SearchQuerySet().models(Page).order_by('doc_pk', 'page'), # '-doc_date', 'doc_type_name', '-doc_version',
    form_class=HighlightedSearchForm,
)


