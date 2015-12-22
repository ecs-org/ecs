# -*- coding: utf-8 -*-
import traceback
from datetime import timedelta

from celery.task import periodic_task
from django.utils.translation import ugettext as _
from django.utils import timezone

from ecs.communication.models import Message
from ecs.communication.mailutils import deliver_to_recipient
from ecs.users.utils import get_full_name
from ecs.utils.celeryutils import translate


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
        try:
            submission = msg.thread.submission
            ec_number = u''
            if submission:
                ec_number = u' ' + submission.get_ec_number_display()
            msg.smtp_delivery_state = 'started'
            msg.save()
            msgid, rawmsg = deliver_to_recipient(
                msg.receiver.email,
                subject=_(u'[ECS{ec_number}] {subject}.').format(ec_number=ec_number, subject=msg.thread.subject),
                message=msg.text,
                from_email=u'{0} <{1}>'.format(get_full_name(msg.sender), msg.return_address),
            )
            msg.smtp_delivery_state = 'success'
            msg.rawmsg_msgid = msgid
            msg.rawmsg = rawmsg.as_string()
        except:
            traceback.print_exc()
            msg.smtp_delivery_state = 'failure'

        msg.save()

