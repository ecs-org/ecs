import os

from django.conf import settings

from ecs import bootstrap
from ecs.pki import openssl
from ecs.pki.models import CertificateAuthority
from ecs.core.models import EthicsCommission


@bootstrap.register(depends_on=('ecs.core.bootstrap.ethics_commissions',))
def setup_ca():
    print('creating dummy CA')
    if not CertificateAuthority.objects.exists():
        ec = EthicsCommission.objects.get(uuid=settings.ETHICS_COMMISSION_UUID)
        subject = '/CN={}/O={}'.format(settings.DOMAIN, ec.name)
        openssl.setup(subject)

    if not os.path.exists(settings.ECS_CA_ROOT):
        os.mkdir(settings.ECS_CA_ROOT)

    ca_cert_path = os.path.join(settings.ECS_CA_ROOT, 'ca.cert.pem')
    with open(ca_cert_path, 'w') as f:
        ca = CertificateAuthority.objects.get()
        f.write(ca.cert)

    openssl.gen_crl()
