import re
from django.core.urlresolvers import reverse

from docutils.core import publish_parts as docutils_publish_parts

DEFAULT_DOCUTILS_SETTINGS = {
    'file_insertion_enabled': 0,
    'raw_enabled': 0,
    'initial_header_level': 2,
}

DOC_REF_RE = re.compile(r':doc:`([^`<]+)(?:<(\w+)>)?`', re.UNICODE)
IMAGE_RE = re.compile(r'\.\.\s+(\|(?P<ref>([^|]+))\|\s+)?image::\s+(?P<target>[a-zA-Z0-9._-]+)', re.UNICODE)

class Linker(object):
    def __init__(self, image_url=None, page_url=None, doc_roles=True, slugdict = None):
        self.targets = {}
        self.images = {}
        self.image_url = image_url or (lambda image: reverse('ecs.help.views.download_attachment', kwargs={'attachment_pk': image.pk}))
        self.page_url = page_url or (lambda page: reverse('ecs.help.views.view_help_page', kwargs={'page_pk': page.pk}))
        self.doc_roles = doc_roles
        self.slug2target_dict = slugdict

    def link(self, source):
        from ecs.help.models import Page, Attachment
        if self.doc_roles:
            for match in DOC_REF_RE.finditer(source):
                target = match.group(2) or match.group(1)
                self.targets[target] = None
            for page in Page.objects.filter(slug__in=self.targets.keys()):
                self.targets[page.slug] = page
            source = DOC_REF_RE.sub(self._replace_ref, source)
        else:
            #non default case for printed version of help
            #this will replace :doc:'name' with :doc:'name <docname>'
            for match in DOC_REF_RE.finditer(source):
                target = match.group(2) or match.group(1)
                self.targets[target] = None
            for page in Page.objects.filter(slug__in=self.targets.keys()):
                self.targets[page.slug] = page
            source = DOC_REF_RE.sub(self._replace_ref4print, source)
            
        for match in IMAGE_RE.finditer(source):
            self.images[match.group('target')] = None
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
        if not page:
            return "**bad reference: '{0}'**".format(target)

        return u'`{0} <{1}>`_'.format(text or page.title, self.page_url(page))
    
    def _replace_ref4print(self, match):
        #we need to leave the :doc: refs as is, but supply them with a title,
        #since not all docs have a title in the generated documentation.
        #see ecs_help2sphinx
        if not match.group(2):
            text = None
            target = match.group(1)
        else:
            text = match.group(1)
            target = match.group(2)
        page = self.targets[target]
        if not page:
            return "**bad reference: '{0}'**".format(target)
        #replace target of the link with knowledge from outside...
        if self.slug2target_dict and self.slug2target_dict.has_key(page.slug):
            if self.slug2target_dict[page.slug] != page.slug:
                page.slug = self.slug2target_dict[page.slug]
        return u':doc:`{0} <{1}>`'.format(text or page.title, page.slug)
        
    def _replace_image(self, match):
        ref = match.group('ref')
        target = match.group('target')
        image = self.images[target]
        if not image:
            return "**bad image reference: '{0}'**".format(target)

        if not ref:
            return '.. image:: {0}'.format(self.image_url(image))
        else:
            return '.. |{0}| image:: {1}'.format(ref, self.image_url(image))


def publish_parts(source):
    linker = Linker()
    source = linker.link(source)
    return docutils_publish_parts(source=source, writer_name="html4css1", settings_overrides=DEFAULT_DOCUTILS_SETTINGS)
