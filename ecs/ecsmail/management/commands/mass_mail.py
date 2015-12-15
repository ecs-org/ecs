from django.conf import settings
from django.core.management.base import BaseCommand

from ecs.ecsmail.utils import deliver_to_recipient
 
class Command(BaseCommand):
    help = 'send a mass communication message from system'
    args = '<userlistfile> <textmessagefile> <subject>'

    def handle(self, userlistfile, messagefile, subject, **options):
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        with open(userlistfile, "r") as f:
            ul = f.readlines()
        
        with open(messagefile, 'r') as m:
            message = m.read()
        
        self.stderr.write("Filter: {0}\n".format(settings.ECSMAIL.get('filter_outgoing_smtp')))
        self.stderr.write("Normal Backend: {0}\n".format(settings.EMAIL_BACKEND))
        self.stderr.write("Limited Backend: {0}\n".format(settings.LIMITED_EMAIL_BACKEND))
         
        for recipient in ul:
            recipient = recipient.rstrip()
            if recipient:
                self.stdout.write(recipient+"\n")
                deliver_to_recipient(recipient, subject, message, from_email)
        
