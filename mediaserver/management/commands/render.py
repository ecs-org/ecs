import os
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    args = '<submission.pdf notification.pdf ...>'
    help = 'renders the specified PDF documents to images'
    option_list = BaseCommand.option_list + (
        make_option('--dir', '-d', action='store_true', dest='dir', help='working directory for reading and writing files'),
    )

    def handle(self, *args, **options):
        for pdf_name in args:
            try:
                fd = open(pdf_name, 'r')
                fd.close()
            except IOError:
                raise CommandError('File "%s" does not exist' % pdf_name)
            render(pdf_name)
            print 'Successfully rendered PDF document "%s"' % pdf_name

