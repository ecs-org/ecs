from django.core.management.base import BaseCommand

from ecs.communication.smtpd import EcsMailReceiver


class Command(BaseCommand):
    help = 'Run receiving SMTP server.'

    def handle(self, *args, **options):
        mail_receiver = EcsMailReceiver()
        mail_receiver.run_loop()
