from optparse import make_option
from django.core.management.base import BaseCommand
from ecs.mediaserver.tasks import do_aging
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--real', action='store_false', dest='dryrun', help='really age(delete) files', default=True),
    )
    def handle(self, **options):
        logging.basicConfig(
            level = logging.DEBUG,
            format = '%(asctime)s %(levelname)s %(message)s',
            )
        
        do_aging(options['dryrun']) # .delay().get()
        
