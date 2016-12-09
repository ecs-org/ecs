#!/usr/bin/env python
import re
import smtpd
import asyncore
import email
import mailbox
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ecs.communication.models import Message
from ecs.communication.mailutils import html2text


class SMTPError(Exception):
    def __init__(self, code, description):
        super().__init__('{} {}'.format(code, description))
        self.code = code
        self.description = description


class EcsMailReceiver(smtpd.SMTPServer):

    # 1MB; this seems a lot, but also includes HTML and inline images.
    MAX_MSGSIZE = 1024 * 1024
    ANSWER_TIMEOUT = 365

    def __init__(self):
        smtpd.SMTPServer.__init__(self, settings.SMTPD_CONFIG['listen_addr'], None,
            data_size_limit=self.MAX_MSGSIZE)
        self.undeliverable_maildir = mailbox.Maildir(
            settings.SMTPD_CONFIG['undeliverable_maildir'])

    def _find_msg(self, recipient):
        msg_uuid, domain = recipient.split('@')

        if domain != settings.SMTPD_CONFIG['domain']:
            raise SMTPError(550, 'Relay access denied')

        m = re.match(r'ecs-([0-9A-Fa-f]{32})$', msg_uuid)
        if m:
            try:
                return Message.objects.get(uuid=m.group(1),
                    timestamp__gt=timezone.now() - timedelta(days=self.ANSWER_TIMEOUT))
            except Message.DoesNotExist:
                pass
        raise SMTPError(553, 'Invalid recipient <{}>'.format(recipient))

    def _get_text(self, msg):
        plain = html = None

        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                plain = part.get_payload()
            elif content_type == 'text/html':
                html = html2text(part.get_payload())
            elif content_type.startswith('multipart/'):
                continue
            else:
                raise SMTPError(554,
                    'Invalid message format - attachment not allowed')

        if not plain and not html:
            raise SMTPError(554, 'Invalid message format - empty message')

        return plain or html

    def process_message(self, peer, mailfrom, rcpttos, data):
        try:
            if len(rcpttos) > 1:
                raise SMTPError(554, 'Too many recipients')

            msg = email.message_from_string(data)
            text = self._get_text(msg)

            orig_msg = self._find_msg(rcpttos[0])
            thread = orig_msg.thread
            thread.messages.filter(
                receiver=orig_msg.receiver,
            ).update(unread=False)
            thread.add_message(orig_msg.receiver, text, rawmsg=data,
                rawmsg_msgid=msg['Message-ID'])

        except SMTPError as e:
            self.undeliverable_maildir.add(data)
            return str(e)

        except Exception as e:
            self.undeliverable_maildir.add(data)
            return '451 Unknown error while processing - try again later'

        return '250 Ok'

    def run_loop(self):
        asyncore.loop()
