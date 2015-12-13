from haystack import indexes
from ecs.help.models import Page

class HelpPageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    anchor = indexes.CharField(model_attr='anchor')
    slug = indexes.CharField(model_attr='slug')

    def get_model(self):
        return Page
