import os, re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist

from ecs.help.models import Page
from ecs.help.utils import Linker


class Inserter:
    def __init__(self, node, depth = 0):
        self.node = node
        self.depth = depth

    def __call__(self, slug, depth):
        newNode = HelpNode(slug)
        if (depth > self.depth):
            self.node.add(newNode)
            self.depth = depth
        elif (depth == self.depth):
            self.node.parent.add(newNode)
        else:
            parent = self.node.parent
            for i in xrange(0, self.depth - depth):
                parent = parent.parent
            parent.add(newNode)
            self.depth = depth

        self.node = newNode


class HelpNode:
    def __init__(self, slug, virtual= False):
        self.slug = slug
        self.parent = None
        self.children = []
        self.title = ''
        self.text = ''
    
        if virtual:
            self.title = 'virtual object: {0}'.format(slug)
        else:
            try:
                page = Page.objects.get(slug = slug)
            except ObjectDoesNotExist:
                self.title = 'missing object: {0}'.format(slug)
            else:
                self.title = page.title
                self.text = page.text
                 
    @classmethod
    def create_root(cls, slug, virtual, linker, output_dir):
        obj = cls(slug, virtual= virtual)
        obj.linker = linker
        obj.output_dir = output_dir
        return obj

    def __iter__(self): 
        yield self
        for child in self.children:
            for node in child.__iter__().next():
                yield node
        
    def root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node
        
    def add(self, child):
        self.children.append(child)
        child.parent = self

    def _page_title(self):
        title = unicode(self.title)
        heading = u''.ljust(len(title), '#')
        pagetitle = u'{heading}\n{title}\n{heading}\n\n\n'.format(heading= heading, title= title)
        return pagetitle

    def _write_file(self, filename, data):
        with open(os.path.join(self.root().output_dir, filename), 'w') as f:
            f.write(data.encode('utf-8'))

    def _write_page(self, include_header):
        linked_text = self.root().linker.link(self.text) 
        fulltext = self._page_title()+ linked_text if include_header else linked_text
        self._write_file('{0}.rst'.format(self.slug), fulltext)
        
    def process_tree(self, depth = 0):
        if len(self.children) == 0:
            self._write_page(True)
            return

        toctree = []
        
        if self.slug == self.root().slug:
            # we do not include the original root index in the fake index
            # we do not write the original root index to disk, and we name our generated one like the original
            filename = '{0}.rst'.format(self.slug)    
        else:
            self._write_page(False)
            toctree.append(self.slug)
            filename = 'fake_{0}.rst'.format(self.slug)

        for child in self.children:
            if len(child.children) > 0:
                toctree.append('fake_{0}'.format(child.slug))
            else:
                toctree.append(child.slug)
            
            child.process_tree(depth= depth + 1)

        toctree = u'.. toctree::\n\n  '+ u'\n  '.join(toctree)+ u'\n\n'
        self._write_file(filename, self._page_title()+ toctree)


def parse_docpages(indexslug, exclude_slugs, output_dir, warn_missing=True):
    ''' takes a slug doc-page as index, include every doc-page that is referenced using line "[space]*\* :doc:" at the beginning
    '''
    MAGIC_REF_RE = re.compile(r'([ ]*)\*[ ]+:doc:`([^`<]+)(?:<(\w+)>)?`', re.UNICODE)
    linker = Linker(
        image_url=lambda img: '../images/%s' % os.path.split(img.file.name)[1],
        doc_roles=False,
    )
    tree = HelpNode.create_root(indexslug, virtual= False, linker= linker, output_dir= output_dir)
    inserter = Inserter(tree)
    
    for match in MAGIC_REF_RE.finditer(tree.text):
        indent = len(match.group(1))
        target = match.group(3) or match.group(2)
        inserter(target, (indent/2+1)) # TODO: fails on indent stepping != 2

    tree.process_tree()
    
    if warn_missing:
        processed = set(node.slug for node in tree)
        all = set(val_list[0] for val_list in Page.objects.values_list('slug'))
        
        for x in all- processed:
            print('Warning: not included docpage: {0}'.format(x))
    

class Command(BaseCommand):
    def handle(self, targetdir=None, **options):
        targetdir = settings.ECSHELP_ROOT if targetdir is None else targetdir
        output_dir = os.path.join(targetdir, 'src')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        parse_docpages('index', [], output_dir)
