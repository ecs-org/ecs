from django.db import models
from django.contrib.auth.models import User


class Certificate(models.Model):
    user = models.ForeignKey(User, related_name='certificates')
    cn = models.CharField(max_length=100, unique=True)
    subject = models.TextField()
    fingerprint = models.CharField(max_length=60)
    serial = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
