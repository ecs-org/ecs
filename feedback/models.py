from django.db import models

# Create your models here.

class Feedback(models.Model):
    FEEDBACK_TYPES=(('i', 'Idea'),('q','Question'))
    feedbacktype = models.CharField(choices=FEEDBACK_TYPES, max_length=1)
    summary= models.CharField(max_length=200) 
    description = models.TextField()
    origin = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    email = models.EmailField()
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

