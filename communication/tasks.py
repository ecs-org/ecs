# -*- coding: utf-8 -*-
import os
import traceback
import hashlib
import time
from datetime import datetime, timedelta

from celery.decorators import task, periodic_task
from celery.task.sets import subtask
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.mail import make_msgid

from ecs.communication.models import Message
from ecs.ecsmail.mail import deliver_to_recipient
from ecs.users.utils import get_full_name


@task()
def update_smtp_delivery(msgid, state, **kwargs):
    logger = update_smtp_delivery.get_logger(**kwargs)
    logger.info('updating status of msg {0} to {1}'.format(msgid, state))

    updated = Message.objects.filter(rawmsg_msgid=msgid).update(smtp_delivery_state=state)
    if not updated == 1:
        logger.error('could not update status of message id {0}, message does not exist'.format(msgid))


@periodic_task(run_every=timedelta(minutes=1))
def forward_messages(**kwargs):
    logger = forward_messages.get_logger(**kwargs)
    messages = Message.objects.filter(
        unread=True,
        smtp_delivery_state='new',
        receiver__ecs_profile__forward_messages_after_minutes__gt=0
    ).select_related('receiver')

    now = datetime.now()
    messages = [m for m in messages if m.timestamp + timedelta(minutes=m.receiver.ecs_profile.forward_messages_after_minutes) <= now]
    if len(messages) == 0:
        return

    logger.info('Forwarding {0} messages'.format(len(messages)))

    for msg in messages:
        try:
            msg.rawmsg_msgid = make_msgid()
            msg.save()
            mail_list = deliver_to_recipient(
                msg.receiver.email,
                subject=_('New ECS-Mail: from {sender} to {receiver}.').format(sender=msg.sender, receiver=msg.receiver),
                message=_('Subject: {subject}{linesep}{text}').format(subject=msg.thread.subject, text=msg.text, linesep=os.linesep),
                from_email='{0} <{1}>'.format(get_full_name(msg.sender), msg.return_address),
                callback=subtask(update_smtp_delivery),
                msgid=msg.rawmsg_msgid,
            )
            msg.smtp_delivery_state = 'pending'
            msg.rawmsg = unicode(mail_list[1])
            msg.rawmsg_digest_hex = hashlib.md5(msg.rawmsg).hexdigest()
        except:
            traceback.print_exc()
            msg.smtp_delivery_state = 'failure'

        msg.save()

