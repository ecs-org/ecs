import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


MESSAGE_ORIGIN_ALICE = 1
MESSAGE_ORIGIN_BOB = 2

DELIVERY_STATES = (
    ("new", "new"),
    ("started", "started"),
    ("success", "success"),
    ("failure", "failure"),
)


class ThreadQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(Q(sender=user) | Q(receiver=user))

    def incoming(self, user):
        return self.filter(
            Q(sender=user, last_message__origin=MESSAGE_ORIGIN_BOB) |
            Q(receiver=user, last_message__origin=MESSAGE_ORIGIN_ALICE)
        )

    def outgoing(self, user):
        return self.filter(
            Q(sender=user, last_message__origin=MESSAGE_ORIGIN_ALICE) |
            Q(receiver=user, last_message__origin=MESSAGE_ORIGIN_BOB)
        )

    def for_widget(self, user):
        return self.filter(
            Q(sender=user, starred_by_sender=True) |
            Q(receiver=user, starred_by_receiver=True) |
            Q(
                Q(sender=user) | Q(receiver=user),
                id__in=Message.objects.filter(receiver=user, unread=True).values('thread_id')
            )
        )


class Thread(models.Model):
    subject = models.CharField(max_length=100)
    submission = models.ForeignKey('core.Submission', null=True)
    # sender, receiver and timestamp are denormalized intentionally
    sender = models.ForeignKey(User, related_name='outgoing_threads')
    receiver = models.ForeignKey(User, related_name='incoming_threads')
    timestamp = models.DateTimeField(auto_now_add=True)
    last_message = models.OneToOneField('Message', null=True, related_name='head')
    related_thread = models.ForeignKey('self', null=True)

    starred_by_sender = models.BooleanField(default=False)
    starred_by_receiver = models.BooleanField(default=False)

    objects = ThreadQuerySet.as_manager()

    def star(self, user):
        if user.id == self.sender_id:
            self.starred_by_sender = True
        elif user.id == self.receiver_id:
            self.starred_by_receiver = True
        else:
            assert False
        self.save()

    def unstar(self, user):
        if user.id == self.sender_id:
            self.starred_by_sender = False
        elif user.id == self.receiver_id:
            self.starred_by_receiver = False
        else:
            assert False
        self.save()

    def add_message(self, user, text, rawmsg_msgid=None, rawmsg=None, reply_receiver=None):
        assert user.id in (self.sender_id, self.receiver_id)

        if user.id == self.sender_id:
            receiver = self.receiver
            origin = MESSAGE_ORIGIN_ALICE
        else:
            receiver = self.sender
            origin = MESSAGE_ORIGIN_BOB

        previous_message = self.last_message
        if previous_message and previous_message.reply_receiver and previous_message.receiver_id == user.id:
            receiver = previous_message.reply_receiver

        while receiver.profile.is_indisposed:
            receiver = receiver.profile.communication_proxy

        if origin == MESSAGE_ORIGIN_ALICE:
            self.receiver = receiver
        else:
            self.sender = receiver

        msg = self.messages.create(
            sender=user,
            receiver=receiver,
            text=text,
            origin=origin,
            smtp_delivery_state='new',
            rawmsg=rawmsg,
            rawmsg_msgid=rawmsg_msgid,
            reply_receiver=reply_receiver
        )
        self.last_message = msg
        self.closed_by_sender = False
        self.closed_by_receiver = False
        self.save()
        return msg

    def delegate(self, from_user, to_user):
        assert from_user.id in (self.sender_id, self.receiver_id)

        if from_user.id == self.sender_id:
            self.sender = to_user
        else:
            self.receiver = to_user

        self.save()

    def get_participants(self):
        return User.objects.filter(Q(outgoing_messages__thread=self) | Q(incoming_messages__thread=self)).distinct()

    def message_list(self):
        return self.messages.order_by('timestamp')


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages')
    sender = models.ForeignKey(User, related_name='outgoing_messages')
    receiver = models.ForeignKey(User, related_name='incoming_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    unread = models.BooleanField(default=True)
    soft_bounced = models.BooleanField(default=False)
    text = models.TextField()

    rawmsg = models.TextField(null=True)
    rawmsg_msgid = models.CharField(max_length=250, null=True, db_index=True)

    origin = models.SmallIntegerField(default=MESSAGE_ORIGIN_ALICE, choices=((MESSAGE_ORIGIN_ALICE, 'Alice'), (MESSAGE_ORIGIN_BOB, 'Bob')))

    smtp_delivery_state = models.CharField(max_length=7,
                            choices=DELIVERY_STATES, default='new',
                            db_index=True)

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)

    reply_receiver = models.ForeignKey(User, null=True, related_name='reply_receiver_for_messages')

    @property
    def return_address(self):
        return 'ecs-{}@{}'.format(self.uuid.hex,
            settings.DOMAIN)
