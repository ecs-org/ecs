import datetime
from django.db import models
from django.contrib.auth.models import User

class Text(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    text = models.TextField()
    author = models.ForeignKey(User)
    ctime = models.DateTimeField(default=datetime.datetime.now)
    mtime = models.DateTimeField()
    
    def save(self, **kwargs):
        self.mtime = datetime.datetime.now()
        return super(Text, self).save(**kwargs)