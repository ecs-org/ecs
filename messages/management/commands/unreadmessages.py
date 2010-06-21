from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from ecs.messages.models import Message
from ecs.utils.datastructures import OrderedSet
from ecs.messages.mail import send_mail

class Command(BaseCommand):
    help = 'Checks for users with unread messages.'

    def handle(self, *args, **options):
        msgs = Message.objects.filter(unread=True)
        for msg in msgs:
            if msg.thread.closed_by_sender or msg.thread.closed_by_receiver:
                msg.unread = False
                msg.save()
        
        msgs = Message.objects.filter(unread=True)
        
        user_digests = {}
        
        for msg in msgs:
            user_digests.setdefault(msg.receiver, OrderedSet()).add(msg)
        
        for user, mails in user_digests.items():
            message = render_to_string('messages/mail/digest.txt', {
                'count': len(mails),
                'mails': mails,
                'user': user,
            })
            print message
            
            send_mail(subject='Ungelesene ECS Nachrichten fuer %s' % (user,), 
                                                             message=message,
                                                             from_email=settings.DEFAULT_FROM_EMAIL,
                      recipient_list=[user.email], fail_silently=False)
            print 'MAIL SENT'