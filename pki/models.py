from django.db import models
from django.contrib.auth.models import User

class Certificate(models.Model):
    user = models.ForeignKey(User, related_name='certificates')
    cn = models.CharField(max_length=100)
    subject = models.TextField()
    fingerprint = models.CharField(max_length=60)
    is_revoked = models.BooleanField(default=False)
    