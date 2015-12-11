import os
from django.conf import settings

from ecs import bootstrap
from ecs.pki import openssl


@bootstrap.register()
def setup_ca():
    if os.path.exists(settings.ECS_CA_ROOT):
        return

    print('creating dummy CA')
    subject_bits = (
        ('CN', 'testecs.local'),
        ('C', 'AT'),
        ('ST', 'Vienna'),
        ('localityName', 'Vienna'),
        ('O', 'ep3 Software & System House'),
        ('OU', 'Security'),
        ('emailAddress', 'admin@testecs.local'),
    )

    subject = ''.join('/%s=%s' % bit for bit in subject_bits)
    fingerprint = openssl.setup(subject)
    print fingerprint
