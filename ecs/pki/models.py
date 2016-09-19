import math
import random
import string

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from ecs.users.utils import get_full_name
from ecs.pki.utils import get_subject


PASSPHRASE_ENTROPY = 80
PASSPHRASE_CHARS = string.ascii_lowercase + string.digits


class Certificate(models.Model):
    user = models.ForeignKey(User, related_name='certificates')
    cn = models.CharField(max_length=100, unique=True)
    subject = models.TextField()
    serial = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)

    @classmethod
    def get_serial(cls):
        last_serial = cls.objects.aggregate(models.Max('serial'))['serial__max']
        return (last_serial or 0) + 1

    @classmethod
    def get_crlnumber(cls):
        return cls.objects.exclude(revoked_at=None).count() + 1

    @classmethod
    def create_for_user(cls, pkcs12, user, cn=None):
        if not cn:
            cn = get_full_name(user)
        subject = get_subject(cn=cn, email=user.email)

        passphrase_len = math.ceil(
            PASSPHRASE_ENTROPY / math.log2(len(PASSPHRASE_CHARS)))
        passphrase = ''.join(
            random.choice(PASSPHRASE_CHARS) for i in range(passphrase_len))

        from ecs.pki import openssl
        data = openssl.make_cert(subject, pkcs12, passphrase=passphrase)
        cert = cls.objects.create(user=user, cn=cn, **data)

        return (cert, passphrase)

    def revoke(self):
        assert self.revoked_at is None
        self.revoked_at = timezone.now()
        self.save()

        from ecs.pki import openssl
        openssl.gen_crl()


class CertificateAuthority(models.Model):
    key = models.TextField()
    cert = models.TextField()
