import sys, os
import re
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

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
    #write title of the page into the rst file, otherwise information is lost
    pagetitle = u"%s%s" % (len(title)*"#", os.linesep)
    pagetitle += u"%s%s" % (title, os.linesep)
    pagetitle += u"%s%s%s%s" % (len(title)*"#", os.linesep, os.linesep, os.linesep)
    return pagetitle

def write_page(slug, include_header, output_dir):
    page = Page.objects.get(slug = slug)
    name = slug + '.rst' 
    title = page_title(page.title)
    
    with open(os.path.join(output_dir, name), 'w') as f:
        fulltext = title+ page.text if include_header else page.text
        f.write(linker.link(fulltext).encode('utf-8'))

def write_toctree(slug, toctree, output_dir):
    page = Page.objects.get(slug = slug)
    name = "fake_"+slug + '.rst' 
    title = page_title(page.title)
    sep = "%s%s"%(os.linesep,'  ')
    toctree = sep.join(toctree)
    toctree = '.. toctree:%s%s%s' % (os.linesep*2,toctree,os.linesep*2)
    with open(os.path.join(output_dir, name), 'w') as f:
        fulltext = title+ toctree
        f.write(linker.link(fulltext).encode('utf-8'))

    
def make_doctree(node, output_dir, depth = 0):
    #print '%s%s' % ('  ' * depth, node.title)
    content = ""
    toctree = []
    
    if len(node.children) == 0:
        #print '%s%s' % ('  ' * depth, node.title)
        write_page(node.title, True, output_dir)
        print "write_page(%s) and header" % node.title
        #write title into document, no further children
    
    else:
        #print '%sfake_%s' % ('  ' * depth, node.title)
        #if depth > 0
        #create fake document, add node title to this document, include "real" document
        write_page(node.title, False, output_dir)
        print "write_page(%s) none header" % node.title
        toctree.append(node.title)
        
        for child in node.children:
            if len(child.children) > 0:
                #print '%schild fake_%s' % ('  ' * depth, child.title)
                toctree.append("fake_%s" % child.title)
            else:
                #print '%schild %s' % ('  ' * depth, child.title)
                toctree.append("%s" % child.title)
            
            make_doctree(child, output_dir, depth= depth + 1)
                
        write_toctree(node.title, toctree, output_dir)
        print "write_page(%s) with header and toctree (%s)" % ("fake_"+node.title, toctree)
       

def parse_index_list(text, output_dir):
    ''' gets every line with "[space]*\* :doc:" at the beginning
    :return: list ((indent,target)*)
    '''
    
    MAGIC_REF_RE = re.compile(r'([ ]*)\*[ ]+:doc:`([^`<]+)(?:<(\w+)>)?`', re.UNICODE)

    tree = Node("index")
    inserter = Inserter(tree)
    
    pagelist = []

    for match in MAGIC_REF_RE.finditer(text):
        indent = len(match.group(1))
        target = match.group(3) or match.group(2)
        #print("Target: {0}, indent {1}".format(target,indent))
        inserter(target, (indent/2+1))

    make_doctree(tree, output_dir)



def generate_sphinx_doctree():
    ''' write the index and doctree pages with glamor '''
    
    fulltext = pagetitle+page.text
    intro=u"""##################
    Inhaltsverzeichnis
    ##################
    
    .. include:: ../../../_latex_head.rst
    .. include:: ../../../_latex_tail.rst
    
    .. toctree::
    :maxdepth: 2
    
    """                 
    indent = '%s   ' % os.linesep
    toctree = indent.join(["%s%s" % (' '*indent, doc) for doc,indent in doclist])
    fulltext = intro + toctree 
    f.write(linker.link(fulltext).encode('utf-8'))
                    


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
        
        pagelist = parse_index_list(Page.objects.get(slug='index'), output_dir)






         
        for page in Page.objects.all():
            if page.slug.lower() != 'index':    
                #use the slug as filename, that way the :doc: directives work
                name = page.slug + '.rst'
                with open(os.path.join(output_dir, name), 'w') as f:
                    #write title of the page into the rst file, otherwise information is lost
                    pagetitle = u"%s%s" % (len(page.title)*"#", os.linesep)
                    pagetitle += u"%s%s" % (page.title, os.linesep)
                    pagetitle += u"%s%s%s%s" % (len(page.title)*"#", os.linesep, os.linesep, os.linesep)
                    
                    #generate toc tree directive for sphinx:
                    #FIXME some paths are hardcoded here and this is not really nicely done
                    fulltext = pagetitle+page.text
                    f.write(linker.link(fulltext).encode('utf-8'))
        
        generate_sphinx_doctree(pagelist, output_dir)
