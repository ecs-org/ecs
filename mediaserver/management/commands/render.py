import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    args = '<submission.pdf notification.pdf ...>'
    help = 'renders the specified PDF document to images'

    def handle(self, *args, **options):
        for pdf_name in args:
            try:
                fd = open(pdf_name, 'r')
            except IOError:
                raise CommandError('File "%s" does not exist' % pdf_name)
            #
            print 'Successfully redered PDF document "%s"' % pdf_name

