from haystack.indexes import *
from haystack import site
from ecs.documents.models import Document, Page

class PageIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    page = IntegerField(model_attr='num')
    doc_pk = IntegerField(model_attr='doc__pk')
    doc_date = DateField(model_attr='doc__date')
    doc_version = CharField(model_attr='doc__version')
    doc_type_name = CharField(model_attr='doc__doctype__name', null=True)

site.register(Page, PageIndex)
