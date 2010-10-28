from django.db import models

class RawMail(models.Model):
    message_digest_hex = models.CharField(max_length=32) 
    ecshash = models.CharField(max_length=32, db_index=True)
    data = models.TextField()
