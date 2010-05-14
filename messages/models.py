import datetime
from django.db import models
from django.contrib.auth.models import User

class MessageQuerySet(models.query.QuerySet):
    def by_user(self, *users):
        return self.filter(models.Q(sender__in=users) | models.Q(receiver__in=users))

class MessageManager(models.Manager):
    def get_query_set(self):
        return MessageQuerySet(self.model)

    def by_user(self, *users):
        return self.all().by_user(*users)
    
class Message(models.Model):
    submission = models.ForeignKey('core.Submission', null=True)
    task = models.ForeignKey('tasks.Task', null=True)
    sender = models.ForeignKey(User, related_name='sent_messages')
    receiver = models.ForeignKey(User, related_name='received_messages')
    reply_to = models.ForeignKey('self', null=True, related_name='replies')
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    unread = models.BooleanField(default=True)
    subject = models.CharField(max_length=100)
    text = models.TextField()
    
    objects = MessageManager()