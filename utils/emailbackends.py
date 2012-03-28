import tempfile
import subprocess
import logging

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from sentry.client.handlers import SentryHandler

class EMLEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        try:
            for message in email_messages:
                with tempfile.NamedTemporaryFile(suffix='.eml') as tmp:
                    tmp.write(message.message().as_string())
                    tmp.flush()
                    subprocess.call(['open', tmp.name])
        except:
            if not self.fail_silently:
                raise
        return len(email_messages)


logger = logging.getLogger(__name__)
logger.addHandler(SentryHandler())
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

class SentryEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        for message in email_messages:
            logger.info(u'Email to {0}: {1}\n\n{2}'.format(u','.join(message.to), message.subject, message.message().as_string()))
