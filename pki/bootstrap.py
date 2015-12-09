import os
from django.conf import settings

from ecs import bootstrap
from ecs.pki.utils import get_ca


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
    ca = get_ca()
    os.makedirs(settings.ECS_CA_ROOT)

    with open(settings.ECS_CA_CONFIG, "w+b") as outputfile:
        with open(os.path.join(settings.PROJECT_DIR, 'templates', 'config', 'openssl-ca.cnf')) as inputfile:
            text = inputfile.read()
        text = text % ca.__dict__
        outputfile.write(text)

    ca.setup(subject)
    print ca.ca_fingerprint
