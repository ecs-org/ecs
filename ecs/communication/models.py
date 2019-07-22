import uuid
import traceback

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.communication.mailutils import deliver_to_recipient
from ecs.users.utils import get_full_name


DELIVERY_STATES = (
    ("new", "new"),
    ("started", "started"),
    ("success", "success"),
    ("failure", "failure"),
)

# https://tools.ietf.org/html/rfc3834
# https://tools.ietf.org/html/rfc5436
CREATOR_CHOICES = (
    ("human", "human"),
    ("auto-self", "auto-self"),
    ("auto-custom", "auto-custom"),
    # rfc3834 compatible
    ("auto-generated", "auto-generated"),
    ("auto-replied", "auto-replied"),
    ("auto-notified", "auto-notified"),
)


class ThreadQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(Q(sender=user) | Q(receiver=user))

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

    starred_by_sender = models.BooleanField(default=False, db_index=True)
    starred_by_receiver = models.BooleanField(default=False, db_index=True)

    objects = ThreadQuerySet.as_manager()

    def star(self, user):
        assert user.id in (self.sender_id, self.receiver_id)
        if user.id == self.sender_id:
            self.starred_by_sender = True
        if user.id == self.receiver_id:
            self.starred_by_receiver = True
        self.save(update_fields=('starred_by_sender', 'starred_by_receiver'))

    def unstar(self, user):
        assert user.id in (self.sender_id, self.receiver_id)
        if user.id == self.sender_id:
            self.starred_by_sender = False
        if user.id == self.receiver_id:
            self.starred_by_receiver = False
        self.save(update_fields=('starred_by_sender', 'starred_by_receiver'))

    def add_message(self, user, text,
                    reply_receiver=None, rawmsg=None,
                    outgoing_msgid=None, incoming_msgid=None,
                    in_reply_to=None, creator=None):
        assert user.id in (self.sender_id, self.receiver_id)

        if user.id == self.sender_id:
            receiver = self.receiver
        else:
            receiver = self.sender

        previous_message = self.last_message
        if previous_message and previous_message.reply_receiver and previous_message.receiver_id == user.id:
            receiver = previous_message.reply_receiver

        while receiver.profile.is_indisposed:
            receiver = receiver.profile.communication_proxy

        if user.id == self.sender_id:
            self.receiver = receiver
        else:
            self.sender = receiver

        if creator is None:
            creator = 'human'

        msg = self.messages.create(
            sender=user,
            receiver=receiver,
            text=text,
            smtp_delivery_state='new',
            rawmsg=rawmsg,
            outgoing_msgid=outgoing_msgid,
            incoming_msgid=incoming_msgid,
            reply_receiver=reply_receiver,
            in_reply_to=in_reply_to,
            creator=creator,
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

    def message_list(self):
        return self.messages.order_by('timestamp')


class Message(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    thread = models.ForeignKey(Thread, related_name='messages')
    sender = models.ForeignKey(User, related_name='outgoing_messages')
    receiver = models.ForeignKey(User, related_name='incoming_messages')
    reply_receiver = models.ForeignKey(User, null=True,
        related_name='reply_receiver_for_messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    unread = models.BooleanField(default=True, db_index=True)
    text = models.TextField()

    rawmsg = models.TextField(null=True)
    outgoing_msgid = models.CharField(max_length=250, null=True)
    incoming_msgid = models.CharField(max_length=250, null=True)

    smtp_delivery_state = models.CharField(max_length=7,
        choices=DELIVERY_STATES, default='new', db_index=True)
    in_reply_to = models.ForeignKey('self', related_name='is_replied_in',
        null=True, default=None)
    creator = models.CharField(max_length=14,
        choices=CREATOR_CHOICES, default='human')

    @property
    def return_address(self):
        return 'ecs-{}@{}'.format(self.uuid.hex, settings.DOMAIN)

    @property
    def smtp_subject(self):
        submission = self.thread.submission
        ec_number = ''
        if submission:
            ec_number = ' ' + submission.get_ec_number_display()
        subject = _('[ECS{ec_number}] {subject}.').format(
            ec_number=ec_number, subject=self.thread.subject)
        return subject

    def forward_smtp(self):
        try:
            forwarded = False
            subject = self.smtp_subject
            headers = {}

            if self.creator in ("human", "auto-self"):
                self.smtp_delivery_state = 'started'
                self.save()

                if self.creator == "auto-self":
                    headers.update({"Auto-Submitted": "auto-generated", })
                else:
                    headers.update({"Auto-Submitted": "auto-replied", })
                if self.incoming_msgid:
                    headers.update({
                        'In-Reply-To': self.incoming_msgid,
                        'References': " ".join((self.incoming_msgid,
                                                self.in_reply_to.outgoing_msgid)),
                    })

                msgid, rawmsg = deliver_to_recipient(
                    self.receiver.email,
                    subject=subject,
                    message=self.text,
                    from_email='{0} <{1}>'.format(get_full_name(self.sender), self.return_address),
                    rfc2822_headers=headers,
                )

                forwarded = True
                self.outgoing_msgid = msgid
                # do not overwrite rawmsg on forward, if it originated from smtp
                if not self.incoming_msgid:
                    self.rawmsg = rawmsg.as_string()

            self.smtp_delivery_state = 'success'
        except:
            traceback.print_exc()
            self.smtp_delivery_state = 'failure'
            raise
        finally:
            self.save()
            return forwarded
