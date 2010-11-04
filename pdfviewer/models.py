import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from ecs.documents.models import Document

class DocumentAnnotation(models.Model):
    user = models.ForeignKey(User, related_name='document_annotations')
    author = models.ForeignKey(User, null=True)
    document = models.ForeignKey(Document, related_name='annotations')
    page_number = models.PositiveIntegerField()
    text = models.TextField(blank=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    
    @property
    def human_readable_location(self):
        y = self.y + self.height / 2
        if y < 1.0/3:
            return _("top")
        elif y < 2.0/3:
            return _("middle")
        else:
            return _("bottom")