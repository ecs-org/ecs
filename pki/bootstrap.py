import os
from django.conf import settings

from ecs import bootstrap
from ecs.pki import openssl
from ecs.pki.models import CertificateAuthority


@bootstrap.register()
def setup_ca():
    print('creating dummy CA')
    if not CertificateAuthority.objects.exists():
        # XXX: use sane data from settings instead
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
        openssl.setup(subject)

    if not os.path.exists(settings.ECS_CA_ROOT):
        os.mkdir(settings.ECS_CA_ROOT)

    ca_cert_path = os.path.join(settings.ECS_CA_ROOT, 'ca.cert.pem')
    with open(ca_cert_path, 'w') as f:
        ca = CertificateAuthority.objects.get()
        f.write(ca.cert)

    openssl.gen_crl()
