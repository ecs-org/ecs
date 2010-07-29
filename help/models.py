from django.db import models
from ecs.tracking.models import View

class Page(models.Model):
    view = models.ForeignKey(View, null=True, blank=True)
    anchor = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=150)
    text = models.TextField()
    
    class Meta:
        unique_together = ('view', 'anchor')
    
class Attachment(models.Model):
    mimetype = models.CharField(max_length=100)
    file = models.FileField(upload_to='help-attachments')
    name = models.CharField(max_length=50)