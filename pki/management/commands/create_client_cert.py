from getpass import getpass
from optparse import make_option
from django.core.management.base import BaseCommand

from ecs.pki.utils import get_ca, get_subject_for_user

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        #make_option('--submission', '-s', dest='submission_pk', action='store', type='int', help="A submission id"),
    )

    def handle(self, email, pkcs12, passphrase=None, days=1, **options):
        ca = get_ca()
        subject = get_subject_for_user(None, cn=email, email=email)
        if passphrase is None:
            passphrase = getpass('Certificate Passphrase: ')
        fingerprint = ca.make_cert(subject, pkcs12, passphrase=passphrase, days=days)
        
