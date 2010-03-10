from django.db import models

# Create your models here.

class DocStash(models.Model):
    key = models.CharField(null=False, max_length=41)
    token = models.AutoField(null=False, primary_key=True)
    value = models.TextField(null=False)
    form = models.CharField(max_length=120, null=False)
    name = models.CharField(max_length=120, null=False)
    modtime = models.DateTimeField(auto_now_add=True)
