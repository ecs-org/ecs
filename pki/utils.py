from django.conf import settings
from ecs.users.utils import get_full_name
from ecs.pki.openssl import CA

def get_ca(**kwargs):
    ca = CA(settings.ECS_CA_ROOT, config=settings.ECS_CA_CONFIG)
    return ca
    
def get_subject_for_user(user, cn=None):
    subject_bits = (
        ('CN', cn or get_full_name(user)),
        ('C', 'AT'),
        ('ST', 'Vienna'),
        ('localityName', 'Vienna'),
        ('O', 'Ethik Komission der med. Uni. Wien'),
        ('OU', 'Internal'),
        ('emailAddress', user.email),
    )
    return ''.join('/%s=%s' % bit for bit in subject_bits)
    