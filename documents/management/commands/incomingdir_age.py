from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from ecs.documents.tasks import age_incoming
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
        
        age_incoming(options['dryrun']) # .delay().get()
        