import tempfile
import subprocess
from django.core.mail.backends.base import BaseEmailBackend


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
