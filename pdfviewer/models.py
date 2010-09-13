import datetime
from django.db import models
from ecs.documents.models import Document

class Annotation(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    layoutData = models.TextField() # JSON
    creation_date = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.datetime.now)
    
    docid = models.ForeignKey(Document, null=True)
    page = models.IntegerField(default=0)