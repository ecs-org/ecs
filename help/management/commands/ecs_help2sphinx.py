import sys, os
import re
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

from ecs.help.models import Page
from ecs.help.utils import Linker


class Command(BaseCommand):
    def handle(self, targetdir=None, **options):
        linker = Linker(
            image_url=lambda img: '../images/%s' % os.path.split(img.file.name)[1],
            doc_roles=False,
        )
        targetdir = settings.ECSHELP_ROOT if targetdir is None else targetdir
        src_dir = os.path.join(targetdir, 'src')
        try:
            os.makedirs(src_dir)
        except:
            pass

        for page in Page.objects.all():
            #use the slug as filename, that way the :doc: directives work
            name = page.slug + '.rst'
            with open(os.path.join(src_dir, name), 'w') as f:
                #write title of the page into the rst file, otherwise information is lost
                pagetitle = u"%s%s" % (len(page.title)*"#", os.linesep)
                pagetitle += u"%s%s" % (page.title, os.linesep)
                pagetitle += u"%s%s%s%s" % (len(page.title)*"#", os.linesep, os.linesep, os.linesep)
                
                #generate toc tree directive for sphinx:
                #FIXME some paths are hardcoded here and this is not really nicely done
                if page.slug.lower() == 'index':
                    doclist = []
                    for line in page.text.splitlines():
                        if ":doc:`" in line:
                            doc = u"ecs-oha/_from_database/src/%s" % line[line.find("`")+1:line.find(" ",line.find("`")+1)]
                            docindent = re.match(r'^\s+', line)
                            if not docindent:
                                docindent = 0
                            else:
                                docindent = docindent.end()
                            doclist.append((doc,docindent))
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
                else:
                    fulltext = pagetitle+page.text
                    f.write(linker.link(fulltext).encode('utf-8'))
        

