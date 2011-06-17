import os, re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist

from ecs.help.models import Page
from ecs.help.utils import Linker


class Node:
    def __init__(self, title):
        self.title = title
        self.parent = None
        self.children = []

    def add(self, child):
        self.children.append(child)
        child.parent = self


class Inserter:
    def __init__(self, node, depth = 0):
        self.node = node
        self.depth = depth

    def __call__(self, title, depth):
        newNode = Node(title)
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


def page_title(title):
    pagetitle = u"%s%s" % (len(title)*"#", os.linesep)
    pagetitle += u"%s%s" % (title, os.linesep)
    pagetitle += u"%s%s%s%s" % (len(title)*"#", os.linesep, os.linesep, os.linesep)
    return pagetitle


def write_page(slug, include_header, output_dir):
    linker = Linker(
            image_url=lambda img: '../images/%s' % os.path.split(img.file.name)[1],
            doc_roles=False,
        )
    try:
        page = Page.objects.get(slug = slug)
    except ObjectDoesNotExist:
        print "missing page %s" % slug
        return
        
    name = slug + '.rst' 
    title = page_title(page.title)
    
    with open(os.path.join(output_dir, name), 'w') as f:
        fulltext = title+ page.text if include_header else page.text
        f.write(linker.link(fulltext).encode('utf-8'))


def write_toctree(slug, toctree, output_dir):
    linker = Linker(
            image_url=lambda img: '../images/%s' % os.path.split(img.file.name)[1],
            doc_roles=False,
        )
    page = Page.objects.get(slug = slug)
    name = "fake_"+slug + '.rst' 
    title = page_title(page.title)
    sep = "%s%s"%(os.linesep,'  ')
    toctree = '  ' + sep.join(toctree)
    toctree = '.. toctree::%s%s%s' % (os.linesep*2,toctree,os.linesep*2)
    with open(os.path.join(output_dir, name), 'w') as f:
        fulltext = title+ toctree
        f.write(linker.link(fulltext).encode('utf-8'))
  

def process_toctree(node, output_dir, depth = 0):
    toctree = []
    
    if len(node.children) == 0:
        print "write_page(%s) and header" % node.title
        write_page(node.title, True, output_dir)
        
    else:
        print "write_page(%s) none header" % node.title
        write_page(node.title, False, output_dir)
        if node.title != 'index':
            # xxx we do not write the real root index to be included in the fake index 
            toctree.append(node.title)
        
        for child in node.children:
            if len(child.children) > 0:
                toctree.append("fake_%s" % child.title)
            else:
                toctree.append("%s" % child.title)
            
            process_toctree(child, output_dir, depth= depth + 1)
                
        print "write_page(%s) with header and toctree (%s)" % ("fake_"+node.title, toctree)
        write_toctree(node.title, toctree, output_dir)
        

def parse_index(text, output_dir):
    ''' gets every line with "[space]*\* :doc:" at the beginning
    :return: list ((indent,target)*)
    '''
    
    MAGIC_REF_RE = re.compile(r'([ ]*)\*[ ]+:doc:`([^`<]+)(?:<(\w+)>)?`', re.UNICODE)
    tree = Node("index")
    inserter = Inserter(tree)
    
    for match in MAGIC_REF_RE.finditer(text):
        indent = len(match.group(1))
        target = match.group(3) or match.group(2)
        inserter(target, (indent/2+1)) # TODO: fails on indent != 2

    process_toctree(tree, output_dir)


"""    
    .. include:: ../../../_latex_head.rst
    .. include:: ../../../_latex_tail.rst
    
    .. toctree::
    :maxdepth: 2
"""    
                    


class Command(BaseCommand):
    def handle(self, targetdir=None, **options):
        linker = Linker(
            image_url=lambda img: '../images/%s' % os.path.split(img.file.name)[1],
            doc_roles=False,
        )
        targetdir = settings.ECSHELP_ROOT if targetdir is None else targetdir
        output_dir = os.path.join(targetdir, 'src')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        parse_index(Page.objects.get(slug='index').text, output_dir)
        
        
        
