import os
import mimetypes

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ecs.utils import cached_property
from ecs.tracking.models import View
from ecs.help.utils import publish_parts


REVIEW_STATUS_CHOICES = (
    ('new', _('New')),
    ('ready_for_review', _('Ready for Review')),
    ('review_ok', _('Review OK')),
    ('review_fail', _('Review Failed')),
)

class Page(models.Model):
    view = models.ForeignKey(View, null=True, blank=True)
    anchor = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=150)
    text = models.TextField()
    review_status = models.CharField(max_length=20, default='new', choices=REVIEW_STATUS_CHOICES)
    
    class Meta:
        unique_together = ('view', 'anchor')
        
    def __unicode__(self):
        return self.title

    @cached_property
    def publish_parts(self):
        return publish_parts(self.text)


class AttachmentFileStorage(FileSystemStorage):
    def path(self, name):
        # We need to overwrite the default behavior, because django won't let us save documents outside of MEDIA_ROOT
        return smart_str(os.path.normpath(name))


def upload_to(instance=None, filename=None):
    instance.original_file_name = os.path.basename(os.path.normpath(filename)) # save original_file_name
    _, file_ext = os.path.splitext(filename)
    target_name = os.path.normpath(os.path.join(settings.ECSHELP_ROOT, 'images', instance.slug))
    return target_name

    
class Attachment(models.Model):
    file = models.FileField(upload_to=upload_to, storage=AttachmentFileStorage())
    mimetype = models.CharField(max_length=100)
    screenshot = models.BooleanField(default=False)
    slug = models.CharField(max_length=100, unique=True, blank=True)
    view = models.ForeignKey(View, null=True, blank=True)
    page = models.ForeignKey(Page, null=True, blank=True)
    
    def save(self, **kwargs):
        if not self.mimetype:
            mimetype, encoding = mimetypes.guess_type(self.file.name)
            self.mimetype = mimetype
        if not self.slug:
            name, ext = os.path.splitext(self.file.name)
            base_slug = slugify(name)
            self.slug = base_slug + ext
            i = 1
            while type(self).objects.filter(slug=self.slug).exists():
                self.slug = '%s_%02d%s' % (base_slug, i, ext)
                i += 1
        return super(Attachment, self).save(**kwargs)
        

import reversion
reversion.register(Page)

def _post_page_delete(sender, **kwargs):
    from haystack import site
    site.get_index(Page).remove_object(kwargs['instance'])
    
def _post_page_save(sender, **kwargs):
    from ecs.help.tasks import index_help_page
    index_help_page.apply_async(args=[kwargs['instance'].pk])

post_delete.connect(_post_page_delete, sender=Page)
post_save.connect(_post_page_save, sender=Page)
