# -*- coding: utf-8 -*-
import datetime, uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from ecs.authorization import AuthorizationManager

MESSAGE_ORIGIN_ALICE = 1
MESSAGE_ORIGIN_BOB = 2

DELIVERY_STATES = (
    ("new", "new"),
    ("received", "received"),
    ("pending", "pending"),
    ("started", "started"),
    ("success", "success"),
    ("failure", "failure"),
    ("retry", "retry"),
    ("revoked", "revoked"),
)


class ThreadQuerySet(models.query.QuerySet):
    def by_user(self, *users):
        return self.filter(models.Q(sender__in=users) | models.Q(receiver__in=users))
        
    def total_message_count(self):
        return Message.objects.filter(thread__in=self.values('pk')).count()
        
    def incoming(self, user):
        return self.filter(models.Q(sender=user, last_message__origin=MESSAGE_ORIGIN_BOB) | models.Q(receiver=user, last_message__origin=MESSAGE_ORIGIN_ALICE))
        
    def outgoing(self, user):
        return self.filter(models.Q(sender=user, last_message__origin=MESSAGE_ORIGIN_ALICE) | models.Q(receiver=user, last_message__origin=MESSAGE_ORIGIN_BOB))
        
    def open(self, user):
        return self.filter(models.Q(closed_by_receiver=False, receiver=user) | models.Q(closed_by_sender=False, sender=user))


class ThreadManager(AuthorizationManager):
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
        
    def incoming(self, user):
        return self.all().incoming(user)
        
    def outgoing(self, user):
        return self.all().outgoing(user)
        
    def open(self, user):
        return self.all().open(user)
        

class MessageQuerySet(models.query.QuerySet):
    def by_user(self, *users):
        return self.filter(models.Q(thread__sender__in=users) | models.Q(thread__receiver__in=users))
        
    def open(self, user):
        return self.filter(models.Q(thread__closed_by_receiver=False, thread__receiver=user) | models.Q(thread__closed_by_sender=False, thread__sender=user))
        
    def outgoing(self, user):
        return self.filter(models.Q(thread__sender=user, origin=MESSAGE_ORIGIN_ALICE) | models.Q(thread__receiver=user, origin=MESSAGE_ORIGIN_BOB))
        
    def incoming(self, user):
        return self.filter(models.Q(thread__sender=user, origin=MESSAGE_ORIGIN_BOB) | models.Q(thread__receiver=user, origin=MESSAGE_ORIGIN_ALICE))
  

class MessageManager(AuthorizationManager):
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
    last_message = models.OneToOneField('Message', null=True, related_name='head')
    related_thread = models.ForeignKey('self', null=True)
    
    closed_by_sender = models.BooleanField(default=False)
    closed_by_receiver = models.BooleanField(default=False)
    
    objects = ThreadManager()

    def mark_closed_for_user(self, user):
        for msg in self.messages.all():
            msg.unread = False
            msg.save()
        
        if user.id == self.sender_id:
            self.closed_by_sender = True
            self.save()
        if user.id == self.receiver_id:
            self.closed_by_receiver = True
            self.save()

    def add_message(self, user, text, reply_to=None, is_received=False, rawmsg_msgid=None, rawmsg=None, rawmsg_digest_hex=None, reply_receiver=None):
        if user.id == self.receiver_id:
            receiver = self.sender
            origin = MESSAGE_ORIGIN_BOB
        elif user.id == self.sender_id:
            receiver = self.receiver
            origin = MESSAGE_ORIGIN_ALICE
        else:
            raise ValueError("Messages for this thread must only be sent from %s or %s. Sender is %s" % (self.sender.email, self.receiver.email, user.email))
        
        if receiver.get_profile().is_indisposed:
            proxy = receiver.get_profile().communication_proxy
            receiver = proxy
            if origin == MESSAGE_ORIGIN_ALICE:
                self.receiver = proxy
            else:
                self.sender = proxy

        # fixme: instead of not sending emails received, we should check if the target user is currently online, and send message only if the is not online
        smtp_delivery_state = "received" if is_received else "new"
        
        msg = self.messages.create(
            sender=user, 
            receiver=receiver, 
            text=text, 
            reply_to=reply_to, 
            origin=origin,
            smtp_delivery_state= smtp_delivery_state,
            rawmsg= rawmsg,
            rawmsg_msgid= rawmsg_msgid,
            rawmsg_digest_hex= rawmsg_digest_hex,
            reply_receiver=reply_receiver
        )
        previous_message = self.last_message
        if previous_message and previous_message.reply_receiver and previous_message.receiver_id == user.id:
            if origin == MESSAGE_ORIGIN_ALICE:
                self.receiver = previous_message.reply_receiver
            else:
                self.sender = previous_message.reply_receiver
        self.last_message = msg
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

    def get_participants(self):
        return User.objects.filter(Q(outgoing_messages__thread=self) | Q(incoming_messages__thread=self)).distinct()

    def message_list(self):
        return self.messages.order_by('timestamp')

    def save(self, **kwargs):
        if self.receiver:
            receiver_profile = self.receiver.get_profile()
            if receiver_profile.is_indisposed:
                self.receiver = receiver_profile.communication_proxy
        return super(Thread, self).save(**kwargs)

class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages')
    sender = models.ForeignKey(User, related_name='outgoing_messages')
    receiver = models.ForeignKey(User, related_name='incoming_messages')
    reply_to = models.ForeignKey('self', null=True, related_name='replies')
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    unread = models.BooleanField(default=True)
    soft_bounced = models.BooleanField(default=False)
    text = models.TextField()
    
    rawmsg = models.TextField(null=True)
    rawmsg_msgid = models.CharField(max_length=250, null=True, db_index=True)
    rawmsg_digest_hex = models.CharField(max_length=32, null=True, db_index=True) 
    
    origin = models.SmallIntegerField(default=MESSAGE_ORIGIN_ALICE, choices=((MESSAGE_ORIGIN_ALICE, 'Alice'), (MESSAGE_ORIGIN_BOB, 'Bob')))
    
    smtp_delivery_state = models.CharField(max_length=7, 
                            choices=DELIVERY_STATES, default='new',
                            db_index=True)
    
    uuid = models.CharField(max_length=32, default=lambda: uuid.uuid4().get_hex(), db_index=True)
    
    reply_receiver = models.ForeignKey(User, null=True, related_name='reply_receiver_for_messages')
    
    objects = MessageManager()
    
    @property
    def return_username(self):
        return 'ecs-%s' % (self.uuid,)
    
    @property
    def return_address(self):
        return '%s@%s' % (self.return_username, settings.ECSMAIL['authoritative_domain'])

