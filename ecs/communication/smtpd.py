#!/usr/bin/env python
import sys
import os
import re
import logging
import smtpd
import asyncore
import email
import mailbox
import base64
from datetime import timedelta

import chardet

from django.conf import settings
from django.utils import timezone

from ecs.communication.models import Message
from ecs.communication.mailutils import html2text

logger = logging.getLogger(__name__)


class SMTPError(Exception):
    def __init__(self, code, description):
        super().__init__('{} {}'.format(code, description))
        self.code = code
        self.description = description


class EcsSMTPChannel(smtpd.SMTPChannel):
    def handle_error(self):
        # Invoke the global exception hook to give raven a chance to report
        # errors to sentry.
        sys.excepthook(*sys.exc_info())
        self.handle_close()


def _get_content(message_part):
    payload = message_part.get_payload(decode=True)
    
    if message_part.get_content_charset() is None:
        charset = chardet.detect(payload)['encoding']
        logger.info(
            'no content charset declared, detection result: {0}'.format(charset))
    else:
        charset = message_part.get_content_charset()

    if charset in ['iso-8859-8-i', 'iso-8859-8-e']:
        # XXX https://bugs.python.org/issue18624
        logger.debug('aliasing charset iso-8859-8 for {0}'.format(charset))
        charset = 'iso-8859-8'

    logger.debug('message-part: type: {0} charset: {1}'.format(
        message_part.get_content_type(), charset))
    content = str(payload, charset, "replace")
    return content


class EcsMailReceiver(smtpd.SMTPServer):
    channel_class = EcsSMTPChannel

    # 1MB; this seems a lot, but also includes HTML and inline images.
    MAX_MSGSIZE = 1024 * 1024
    ANSWER_TIMEOUT = 365

    def __init__(self):
        smtpd.SMTPServer.__init__(self, settings.SMTPD_CONFIG['listen_addr'], None,
            data_size_limit=self.MAX_MSGSIZE, decode_data=False)
        self.logger = logging.getLogger('EcsMailReceiver')
        self.store_exceptions = settings.SMTPD_CONFIG.get('store_exceptions', False)
        if self.store_exceptions:
            self.undeliverable_maildir = mailbox.Maildir(
                os.path.join(settings.PROJECT_DIR, '..', 'ecs-undeliverable'))

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
            if content_type.startswith('multipart/'):
                continue
            elif content_type == 'text/plain':
                logger.debug('message: message-part: text/plain')
                plain = _get_content(part)
            elif content_type == 'text/html':
                logger.debug('message: message-part: text/html')
                html = html2text(_get_content(part))
            else:
                raise SMTPError(554,
                    'Invalid message format - invalid content type {0}'.format(
                    part.get_content_type()))
    
        if not plain and not html:
            raise SMTPError(554, 'Invalid message format - empty message')

        text = plain or html
        return text

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        try:
            if len(rcpttos) > 1:
                raise SMTPError(554, 'Too many recipients')

            msg = email.message_from_bytes(data)
            text = self._get_text(msg)
            orig_msg = self._find_msg(rcpttos[0])
            thread = orig_msg.thread
            # XXX: rawmsg can include multiple content-charsets and should be a binaryfield
            # as a workaround we convert to base64
            thread.messages.filter(
                receiver=orig_msg.receiver).update(unread=False)
            thread_msg = thread.add_message(orig_msg.receiver, text,
                rawmsg=base64.b64encode(data),
                rawmsg_msgid=msg['Message-ID'])
            logger.info(
                'Accepted email from {0} via {1} to {2} id {3} thread {4} orig_msg {5} message {6}'.format(
                mailfrom, orig_msg.receiver.email, orig_msg.sender.email, 
                msg['Message-ID'], thread.pk, orig_msg.pk, thread_msg.pk))
            
        except SMTPError as e:
            logger.info('Rejected email: {0}'.format(e))
            return str(e)

        except Exception as e:
            logger.error('email raised exception: {0}'.format(e))
            if self.store_exceptions:
                self.undeliverable_maildir.add(data)
            raise

        return '250 Ok'

    def run_loop(self):
        asyncore.loop()
