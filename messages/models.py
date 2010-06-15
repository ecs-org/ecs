import datetime, uuid
import traceback
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from ecs.messages.mail import send_mail


MESSAGE_ORIGIN_ALICE = 1
MESSAGE_ORIGIN_BOB = 2

DELIVERY_STATES = (
    ("new", "new"),
    ("sent", "sent"),
    ("failed", "failed"),
    ("skipped", "skipped"),
)


class ThreadQuerySet(models.query.QuerySet):
    def by_user(self, *users):
        return self.filter(models.Q(sender__in=users) | models.Q(receiver__in=users))
        
    def total_message_count(self):
        return Message.objects.filter(thread__in=self.values('pk')).count()
        
class ThreadManager(models.Manager):
    def get_query_set(self):
        return ThreadQuerySet(self.model)

    def by_user(self, *users):
        return self.all().by_user(*users)

    def create(self, **kwargs):
        text = kwargs.pop('text', None)
        thread = super(ThreadManager, self).create(**kwargs)
        if text:
            thread.add_message(kwargs['sender'], text)
        return thread
        
class MessageQuerySet(models.query.QuerySet):
    def by_user(self, *users):
        return self.filter(models.Q(thread__sender__in=users) | models.Q(thread__receiver__in=users))
        
    def open(self, user):
        return self.filter(models.Q(thread__closed_by_receiver=False, thread__receiver=user) | models.Q(thread__closed_by_sender=False, thread__sender=user))
        
    def outgoing(self, user):
        return self.filter(models.Q(thread__sender=user, origin=MESSAGE_ORIGIN_ALICE) | models.Q(thread__receiver=user, origin=MESSAGE_ORIGIN_BOB))
        
    def incoming(self, user):
        return self.filter(models.Q(thread__sender=user, origin=MESSAGE_ORIGIN_BOB) | models.Q(thread__receiver=user, origin=MESSAGE_ORIGIN_ALICE))
        
    

class MessageManager(models.Manager):
    def get_query_set(self):
        return MessageQuerySet(self.model)

    def by_user(self, *users):
        return self.all().by_user(*users)
        
    def incoming(self, user):
        return self.all().incoming(user)
        
    def outgoing(self, user):
        return self.all().outgoing(user)


class Thread(models.Model):
    subject = models.CharField(max_length=100)
    submission = models.ForeignKey('core.Submission', null=True)
    task = models.ForeignKey('tasks.Task', null=True)
    # sender, receiver and timestamp are denormalized intentionally
    sender = models.ForeignKey(User, related_name='outgoing_threads')
    receiver = models.ForeignKey(User, related_name='incoming_threads')
    timestamp = models.DateTimeField(default=datetime.datetime.now)

    closed_by_sender = models.BooleanField(default=False)
    closed_by_receiver = models.BooleanField(default=False)
    
    objects = ThreadManager()

    def mark_closed_for_user(self, user):
        if user.id == self.sender_id:
            self.closed_by_sender = True
            self.save()
        elif user.id == self.receiver_id:
            self.closed_by_receiver = True
            self.save()

    def add_message(self, user, text, reply_to=None):
        if user.id == self.receiver_id:
            receiver = self.sender
            origin = MESSAGE_ORIGIN_BOB
        elif user.id == self.sender_id:
            receiver = self.receiver
            origin = MESSAGE_ORIGIN_ALICE
        else:
            raise ValueError("Messages for this thread must only be sent from %s or %s." % (self.sender, self.receiver))
        msg = self.messages.create(
            sender=user, 
            receiver=receiver, 
            text=text, 
            reply_to=reply_to, 
            origin=origin,
        )
        if self.closed_by_sender or self.closed_by_receiver:
            self.closed_by_sender = False
            self.closed_by_receiver = False
            self.save()
        return msg

    def delegate(self, from_user, to_user):
        if from_user.id == self.sender_id:
            self.sender = to_user
        elif from_user.id == self.receiver_id:
            self.receiver = to_user
        else:
            raise ValueError("Threads may only be delegated by the current sender or receiver")
        self.save()


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages')
    sender = models.ForeignKey(User, related_name='outgoing_messages')
    receiver = models.ForeignKey(User, related_name='incoming_messages')
    reply_to = models.ForeignKey('self', null=True, related_name='replies')
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    unread = models.BooleanField(default=True)
    text = models.TextField()
    origin = models.SmallIntegerField(default=MESSAGE_ORIGIN_ALICE, choices=((MESSAGE_ORIGIN_ALICE, 'Alice'), (MESSAGE_ORIGIN_BOB, 'Bob')))
    
    smtp_delivery_state = models.CharField(max_length=7, 
                            choices=DELIVERY_STATES, default='new',
                            db_index=True)
    
    uuid = models.CharField(max_length=32, default=lambda: uuid.uuid4().hex, db_index=True)
    
    objects = MessageManager()
    
    @property
    def return_username(self):
        return 'ecs-%s' % (self.uuid,)
    
    @property
    def return_address(self):
        return '%s@%s' % (self.return_username, settings.DEFAULT_FROM_DOMAIN)
    
    def save(self, *args, **kwargs):
        if self.smtp_delivery_state=='new':
            try:
                send_mail(subject='Neue ECS-Mail: von %s an %s.' % (self.sender, self.receiver), 
                                                                 message='Betreff: %s\r\n%s' % (self.thread.subject, self.text),
                                                                 from_email=self.return_address,
                          recipient_list=[self.receiver.email], fail_silently=False)
                self.smtp_delivery_state='sent'
                super(Message, self).save(*args, **kwargs)
            except:
                traceback.print_exc()
                self.smtp_delivery_state='failed'
                super(Message, self).save(*args, **kwargs)
