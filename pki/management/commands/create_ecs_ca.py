import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
 
from ecs.pki.utils import get_ca

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, cn, o, email, **options):
        if os.path.exists(settings.ECS_CA_ROOT):
            print("Error: {0} already exists, refusing to overwrite".format(settings.ECS_CA_ROOT))
            return

        subject_bits = (
            ('CN', cn),
            ('C', 'AT'),
            ('ST', 'Vienna'),
            ('localityName', 'Vienna'),
            ('O', o),
            ('OU', 'Security'),
            ('emailAddress', email),
        )
    
        subject = ''.join('/%s=%s' % bit for bit in subject_bits)
        ca = get_ca()
        ca.setup(subject)
        print ca.ca_fingerprint
