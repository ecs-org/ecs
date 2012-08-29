import os
import shutil
from django.conf import settings

from ecs import bootstrap
from ecs.pki.utils import get_ca


@bootstrap.register()
def setup_ca():
    if os.path.exists(settings.ECS_CA_ROOT):
        oldcnf = os.path.join(settings.ECS_CONFIG_DIR, 'openssl-ca.cnf')
        newcnf = settings.ECS_CA_CONFIG

        if not os.path.exists(newcnf):
            if os.path.exists(oldcnf):
                print("Warning: Upgrading: Moving openssl-ca.cnf from old to new location")
                shutil.copy(oldcnf, newcnf)
                if os.path.exists(oldcnf+ '.old'):
                    os.remove(oldcnf+ '.old')
                os.rename(oldcnf, oldcnf+".old")
            else:
                print("Error: ECS_CA_ROOT exists, but ECS_CA_CONFIG not found")

    else:
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
        ca.setup(subject)
        print ca.ca_fingerprint
