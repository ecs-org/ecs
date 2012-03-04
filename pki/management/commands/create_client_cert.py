import datetime, sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from ecs.pki.utils import get_ca, get_subject_for_user
from ecs.pki.models import Certificate

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        #make_option('--submission', '-s', dest='submission_pk', action='store', type='int', help="A submission id"),
    )

    def handle(self, email, pkcs12, passphrase=None, days=1, **options):
        ca = get_ca()
        subject = get_subject_for_user(None, cn=email, email=email)
        fingerprint = ca.make_cert(subject, pkcs12, passphrase=passphrase if passphrase else raw_input('Passphrase:'), days=days)
        