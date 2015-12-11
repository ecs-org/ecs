import os
from django.core.management.base import BaseCommand
from django.conf import settings
 
from ecs.pki import openssl

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, cn, o, c, st, email, **options):
        if os.path.exists(settings.ECS_CA_ROOT):
            print("Error: {0} already exists, refusing to overwrite".format(settings.ECS_CA_ROOT))
            return

        subject_bits = (
            ('CN', cn),
            ('C', c),
            ('ST', st),
            ('localityName', st),
            ('O', o),
            ('OU', 'Security'),
            ('emailAddress', email),
        )

        subject = ''.join('/%s=%s' % bit for bit in subject_bits)
        fingerprint = openssl.setup(subject)
        print fingerprint
