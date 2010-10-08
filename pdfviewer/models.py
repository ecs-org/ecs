import datetime
from django.db import models
from django.contrib.auth.models import User
from ecs.documents.models import Document

class DocumentAnnotation(models.Model):
    user = models.ForeignKey(User)
    document = models.ForeignKey(Document, related_name='annotations')
    page_number = models.PositiveIntegerField()
    text = models.TextField(blank=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()