import os
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from ecs.mediaserver.analyzer import Analyzer
from ecs.mediaserver.imageset import ImageSet
from ecs.mediaserver.renderer import Renderer


class Command(BaseCommand):
    args = '<submission.pdf notification.pdf ...>'
    help = 'renders the specified PDF documents to images'
    option_list = BaseCommand.option_list + (
        make_option('--nc', action='store_true', dest='nc', default=False, help='do NOT use zlib compression for the PNG images'),
        make_option('--ni', action='store_true', dest='ni', default=False, help='do NOT use Adam7 interlacing for the PNG images'),
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError('No PDF file names were provided')

        print 'Rendering %s file(s) ..' % len(args)
        for pdf_name in args:
            try:
                f = open(pdf_name, 'rb')
                f.close()
            except IOError:
                raise CommandError('File "%s" does not exist' % pdf_name)

            analyzer = Analyzer()
            analyzer.sniff(pdf_name)
            if analyzer.valid is False:
                raise CommandError('File "%s" is not valid' % pdf_name)
            pages = analyzer.pages
            print '"%s" seems valid, having %s page(s)' % (pdf_name, pages)
           
            image_set = ImageSet(0, pages)

            opt_compress = not options['nc']
            opt_interlace = not options['ni']

            renderer = Renderer()
            renderer.render(pdf_name, image_set, opt_compress, opt_interlace)

        print 'done'

