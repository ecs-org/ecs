#!/usr/bin/env python
import re
import smtpd
import asyncore
import email
import mailbox

from django.conf import settings

from ecs.communication.models import Message
from ecs.communication.mailutils import html2text


class SMTPError(Exception):
    def __init__(self, code, description):
        super(SMTPError, self).__init__('{} {}'.format(code, description))
        self.code = code
        self.description = description


class EcsMailReceiver(smtpd.SMTPServer):
    def __init__(self):
        smtpd.SMTPServer.__init__(self, settings.ECSMAIL['addr'], None)
        self.undeliverable_maildir = mailbox.Maildir(
            settings.ECSMAIL['undeliverable_maildir'])

    def _find_msg(self, recipient):
        msg_uuid, domain = recipient.split('@')

        if domain != settings.ECSMAIL['authoritative_domain']:
            raise SMTPError(550, 'Relay access denied')

        m = re.match(r'ecs-([0-9A-Fa-f]{32})$', msg_uuid)
        if m:
            try:
                return Message.objects.get(uuid=m.group(1))
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
        if len(data) > 1024 * 1024:
            # XXX: Don't add the message to the undeliverable maildir to
            # prevent disk space exhaustion.
            return '552 Message too large (> 1MB)'

        try:
            if len(rcpttos) > 1:
                raise SMTPError(554, 'Too many recipients')

            msg = email.message_from_string(data)
            text = self._get_text(msg)

            orig_msg = self._find_msg(rcpttos[0])
            orig_msg.thread.add_message(orig_msg.receiver, text,
                reply_to=orig_msg, rawmsg=data, rawmsg_msgid=msg['Message-ID'])

        except SMTPError as e:
            self.undeliverable_maildir.add(data)
            return str(e)

        except Exception as e:
            self.undeliverable_maildir.add(data)
            return '451 Unknown error while processing - try again later'

        return '250 Ok'

    def run_loop(self):
        asyncore.loop()
