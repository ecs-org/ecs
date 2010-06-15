from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Feedback(models.Model):
    FEEDBACK_TYPES=(('i', 'Idea'),('q','Question'),('p', 'Problem'),('l','Praise'))
    feedbacktype = models.CharField(choices=FEEDBACK_TYPES, max_length=1)
    summary = models.CharField(max_length=200) 
    description = models.TextField()
    origin = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name='author', null=True)
    pub_date = models.DateTimeField('date published')
    me_too_votes = models.ManyToManyField(User, null=True, blank=True)


