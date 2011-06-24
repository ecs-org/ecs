from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ecs.communication.models import Thread
from ecs.users.utils import get_user

def send_submission_message(submission, subject, text, recipients, email='root@example.org'):
    for recipient in recipients:
        thread, created = Thread.objects.get_or_create(
            subject=subject,
            sender=get_user(email),
            receiver=recipient,
            submission=submission
        )
        message = thread.add_message(get_user(email), text=text)
