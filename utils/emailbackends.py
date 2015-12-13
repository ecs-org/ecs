import logging

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from sentry.client.handlers import SentryHandler


logger = logging.getLogger(__name__)
logger.addHandler(SentryHandler())
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

class SentryEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for message in email_messages:
            logger.info(u'Email to {0}: {1}\n\n{2}'.format(u','.join(message.to), message.subject, message.message().as_string()))
