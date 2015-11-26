import logging

from django.core.management.base import BaseCommand

from ecs.integration.tasks import age_tempfile_dir


class Command(BaseCommand):
    def handle(self, **options):
        logging.basicConfig(
            level = logging.DEBUG,
            format = '%(asctime)s %(levelname)s %(message)s',
            )
        
        age_tempfile_dir() # .delay().get()
