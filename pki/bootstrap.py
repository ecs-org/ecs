import os
from django.conf import settings

from ecs import bootstrap
from ecs.pki.utils import get_ca


@bootstrap.register()
def setup_ca():
    if os.path.exists(settings.ECS_CA_ROOT):
        return

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
    ca = get_ca()
    ca.setup(subject)
    print ca.ca_fingerprint
