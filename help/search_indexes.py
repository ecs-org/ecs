from haystack.indexes import *
from haystack import site
from ecs.help.models import Page

class HelpPageIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title')
    anchor = CharField(model_attr='anchor')
    slug = CharField(model_attr='slug')

site.register(Page, HelpPageIndex)
