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
        make_option('--dir', '-d', action='store_true', dest='dir', help='working directory for reading and writing files'),
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError('No PDF file names were provided')

        print 'Rendering %s file(s) ..' % len(args)
        for pdf_name in args:
            try:
                fd = open(pdf_name, 'r')
                fd.close()
            except IOError:
                raise CommandError('File "%s" does not exist' % pdf_name)

            analyzer = Analyzer()
            analyzer.sniff(pdf_name)
            if analyzer.valid is False:
                raise CommandError('File "%s" is not valid' % pdf_name)
            pages = analyzer.pages
            print '"%s" seems valid, having %s page(s)' % (pdf_name, pages)
           
            image_set = ImageSet(0, pages)

            renderer = Renderer()
            renderer.render(pdf_name, image_set)

        print 'done'

