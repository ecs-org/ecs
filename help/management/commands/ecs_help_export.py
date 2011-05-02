from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.help import serializer 

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-o', action='store', dest='outfile', help='output file', default=None),
    )
    def handle(self, **options):
        if not options['outfile']: 
            raise CommandError('Error: Outputfile "-o filename" must be specified')
        f = file(options['outfile'], 'wb')
        serializer.export(f) 
        f.close()
                

