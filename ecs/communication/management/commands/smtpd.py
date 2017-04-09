import logging

from django.core.management.base import BaseCommand

from ecs.communication.smtpd import EcsMailReceiver


log2level = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 
    'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL}


class Command(BaseCommand):
    help = 'Run receiving SMTP server.'
    
    def add_arguments(self, parser):
        parser.add_argument('-l', '--loglevel', action='store',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            dest='loglevel', default='info', help='set loglevel'
        )

    def handle(self, **options):
        logging.basicConfig(
            level = log2level[options['loglevel'].upper()],
            format = '%(levelname)s %(message)s',
        )
        mail_receiver = EcsMailReceiver()
        mail_receiver.run_loop()
