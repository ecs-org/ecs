from datetime import timedelta

from celery.task import periodic_task
from django.utils import timezone

from ecs.communication.models import Message
from ecs.utils.celeryutils import translate

# run once every minute
@periodic_task(run_every=timedelta(minutes=1))
@translate
def forward_messages():
    logger = forward_messages.get_logger()
    messages = Message.objects.filter(
        unread=True,
        smtp_delivery_state='new',
        receiver__profile__forward_messages_after_minutes__gt=0
    ).select_related('receiver')

    now = timezone.now()
    messages = [m for m in messages if m.timestamp + timedelta(minutes=m.receiver.profile.forward_messages_after_minutes) <= now]
    if len(messages) == 0:
        return

    logger.info('Forwarding {0} messages'.format(len(messages)))

    for msg in messages:
        forwarded = msg.forward_smtp()
        if forwarded:
            if msg.incoming_msgid:
                logger.info('Forward from {0} (in reply to {1} , {2}) to {3} (as {4}) about {5}'.format(
                            msg.sender.email, msg.incoming_msgid,
                            msg.in_reply_to.outgoing_msgid, msg.receiver.email,
                            msg.outgoing_msgid, msg.smtp_subject))
            else:
                logger.info('Forward from {0} to {1} (as {2}) about {3}'.format(
                            msg.sender.email, msg.receiver.email,
                            msg.outgoing_msgid, msg.smtp_subject))
        else:
            logger.info('Not forwarding ({0}) {1}: {2}'.format(
                        msg.creator, msg.receiver.email, msg.smtp_subject))
