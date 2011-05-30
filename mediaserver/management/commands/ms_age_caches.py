from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from ecs.mediaserver.tasks import do_aging
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--real', action='store_false', dest='dryrun', help='really age(delete) files', default=True),
    )
    def handle(self, **options):
        logger = logging.getLogger()
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        do_aging(options['dryrun']) # .delay().get()
        