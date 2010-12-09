import re
from django.core.urlresolvers import reverse

from docutils.core import publish_parts as docutils_publish_parts
from docutils.parsers.rst import roles
from docutils import nodes

DEFAULT_DOCUTILS_SETTINGS = {
    'file_insertion_enabled': 0,
    'raw_enabled': 0,
    'initial_header_level': 2,
}

DOC_REF_RE = re.compile(r':doc:`([^`<]+)(?:<(\w+)>)?`', re.UNICODE)
IMAGE_RE = re.compile(r'\.\. image:: ([a-zA-Z0-9._-]+)', re.UNICODE)

class Linker(object):
    def __init__(self, image_url=None, page_url=None, doc_roles=True):
        self.targets = {}
        self.images = {}
        self.image_url = image_url or (lambda image: reverse('ecs.help.views.download_attachment', kwargs={'attachment_pk': image.pk}))
        self.page_url = page_url or (lambda page: reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))
        self.doc_roles = doc_roles

    def link(self, source):
        from ecs.help.models import Page, Attachment
        if self.doc_roles:
            for match in DOC_REF_RE.finditer(source):
                target = match.group(2) or match.group(1)
                self.targets[target] = None
            for page in Page.objects.filter(slug__in=self.targets.keys()):
                self.targets[page.slug] = page
            source = DOC_REF_RE.sub(self._replace_ref, source)

        for match in IMAGE_RE.finditer(source):
            self.images[match.group(1)] = None
        for image in Attachment.objects.filter(slug__in=self.images.keys()):
            self.images[image.slug] = image
        source = IMAGE_RE.sub(self._replace_image, source)
        return source

    def _replace_ref(self, match):
        if not match.group(2):
            text = None
            target = match.group(1)
        else:
            text = match.group(1)
            target = match.group(2)
        page = self.targets[target]
        if page:
            if not text:
                text = page.title
            return u'`%s <%s>`_' % (text, self.page_url(page))
        return "**bad reference: '%s'**" % target
        
    def _replace_image(self, match):
        target = match.group(1)
        image = self.images[target]
        if image:
            return '.. image:: %s' % self.image_url(image)
        return "**bad image reference: '%s'**" % target
        

def publish_parts(source):
    linker = Linker()
    source = linker.link(source)
    return docutils_publish_parts(source=source, writer_name="html4css1", settings_overrides=DEFAULT_DOCUTILS_SETTINGS)
