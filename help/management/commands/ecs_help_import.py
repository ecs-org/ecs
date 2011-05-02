from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.help import serializer 

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', action='store', dest='infile', help='input file', default=None),
    )
    def handle(self, **options):
        if not options['infile']: 
            raise CommandError('Error: Inputfile "-i filename" must be specified')
        f = file(options['infile'], 'rb')
        serializer.load(f) 
        f.close()

