from getpass import getpass
from django.core.management.base import BaseCommand

from ecs.pki import openssl
from ecs.pki.utils import get_subject

class Command(BaseCommand):
    def handle(self, email, pkcs12, passphrase=None, days=1, **options):
        subject = get_subject(email, email)
        if passphrase is None:
            passphrase = getpass('Certificate Passphrase: ')

        # XXX: We don't keep records of certificates generated with this
        # management command.
        openssl.make_cert(subject, pkcs12, passphrase=passphrase, days=days)
