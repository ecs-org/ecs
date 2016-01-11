from django.db import models
from django.contrib.auth.models import User


class Text(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    text = models.TextField()
    author = models.ForeignKey(User)
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
