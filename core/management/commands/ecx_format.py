import codecs
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.template import Context

from ecs.core.serializer import Serializer
from ecs.utils.viewutils import render_pdf_context


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-o', action='store', dest='outfile', help='output file', default=None),
        make_option('-t', dest='output_type', action='store', default='html', 
        help="""--type can be one of 'html' or 'pdf'
-o outputfile"""),
    )

    def handle(self, **options):
        if options['output_type'] not in ['html', 'pdf']:
            raise CommandError('Error: --type must be one of "html", "pdf"')
        if not options['outfile']: 
            raise CommandError('Error: Outputfile "-o filename" must be specified')
        
        ecxf = Serializer()
        
        if options['output_type'] == "html":
            tpl = get_template('docs/ecx/base.html')
            
            with open(options['outfile'], 'wb') as f:
                f.write(tpl.render(Context({
                    'version': ecxf.version,
                    'fields': ecxf.docs(),
                    })).encode('utf-8'))
        
        else:
            with open(options['outfile'], 'wb') as f:                
                f.write(render_pdf_context('docs/ecx/base.html', {
                    'version': ecxf.version,
                    'fields': ecxf.docs(),
                    }))
