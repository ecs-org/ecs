from django.db import models


class Comment(models.Model):
    submission = models.ForeignKey('core.Submission')
    author = models.ForeignKey('auth.User')
    timestamp = models.DateTimeField(auto_now=True)
    text = models.TextField()
