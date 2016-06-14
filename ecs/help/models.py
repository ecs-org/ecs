from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion

from ecs.utils import cached_property
from ecs.tracking.models import View
from ecs.help.utils import publish_parts


REVIEW_STATUS_CHOICES = (
    ('new', _('New')),
    ('ready_for_review', _('Ready for Review')),
    ('review_ok', _('Review OK')),
    ('review_fail', _('Review Failed')),
)

@reversion.register
class Page(models.Model):
    view = models.ForeignKey(View, null=True, blank=True)
    anchor = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=150)
    text = models.TextField()
    review_status = models.CharField(max_length=20, default='new', choices=REVIEW_STATUS_CHOICES)
    
    class Meta:
        unique_together = ('view', 'anchor')
        
    def __str__(self):
        return self.title

    @cached_property
    def publish_parts(self):
        return publish_parts(self.text)

    @cached_property
    def nav(self):
        from ecs.help.utils import parse_index, ParseError
        def _flatten(tree):
            for el in tree:
                if isinstance(el, list):
                    for sub in _flatten(el):
                        yield sub
                else:
                    yield el

        def _find_top(tree, top=None):
            top = top or []
            for i, el in enumerate(tree):
                prev = None
                try:
                    prev = [e for e in tree[:i] if not isinstance(e, list)][-1]
                except IndexError:
                    pass
                if isinstance(el, list):
                    ret = _find_top(el, top=top + [prev])
                    if ret:
                        return ret
                elif el == self:
                    return top
            return None

        try:
            tree = parse_index()
        except ParseError:
            return None

        top = _find_top(tree)

        pages = list(_flatten(tree))
        prev = next = None
        if self in pages:
            pos = pages.index(self)
            if pos > 0:
                prev = pages[pos-1]
            if pos < len(pages)-1:
                next = pages[pos+1]

        return {'top': top, 'prev': prev, 'next': next}


class Attachment(models.Model):
    content = models.BinaryField()
    mimetype = models.CharField(max_length=100)
    is_screenshot = models.BooleanField(default=False)
    slug = models.CharField(max_length=100, unique=True, blank=True)
    view = models.ForeignKey(View, null=True, blank=True)
    page = models.ForeignKey(Page, null=True, blank=True)


def _post_page_delete(sender, **kwargs):
    from ecs.help.search_indexes import HelpPageIndex
    HelpPageIndex().remove_object(kwargs['instance'])
    
def _post_page_save(sender, **kwargs):
    from ecs.help.tasks import index_help_page
    index_help_page.apply_async(args=[kwargs['instance'].pk])

post_delete.connect(_post_page_delete, sender=Page)
post_save.connect(_post_page_save, sender=Page)
