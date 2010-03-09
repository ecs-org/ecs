from django.db import models

# Create your models here.

class DocStash(models.Model):
    key = models.IntegerField(null=False)
    token = models.IntegerField(null=False, primary_key=True)
    value = models.TextField(null=False)
    form = models.CharField(max_length=120, null=False)
    name = models.CharField(max_length=120, null=False)

