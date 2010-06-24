import logging
import re
from lamson.routing import route, route_like, stateless
from lamson import view, queue
from lamson.bounce import bounce_to
from lamson.server import SMTPError

from django.conf import settings
from ecs.messages.models import Message

from ecs.ecsmail.persil import whitewash

@route(".+")
def IGNORE_BOUNCE(message):
    print "JUST A SOFT BOUNCE", message
    bounces = queue.Queue(settings.BOUNCES)
    bounces.push(message)
    return START

@route(".+")
def NOTIFY_BOUNCE(message):
    print "REALLY HANDLING BOUNCE", message
    bounces = queue.Queue(settings.BOUNCES)
    bounces.push(message)
    return START

@route("(address)@(host)", address=".+")
@bounce_to(soft=IGNORE_BOUNCE, hard=NOTIFY_BOUNCE)
@stateless
def START(message, address=None, host=None):
    from ecs.ecsmail.config.settings import relay
        
    muuid = None
    if host == settings.FROM_DOMAIN: # we acccept mail for this address
        logging.info('PREBLUB %s' % (address,))
        mat = re.match('ecs-([^@]+)', address)
        m = None
        if mat:
            groups = mat.groups()
            if groups:
                muuid = groups[0]
                try:
                    m = Message.objects.get(uuid=muuid)
                except:
                    pass
                
        if not m:
            raise SMTPError(511)
        
        logging.info('REPLY %s %s %s %s %s' % ( muuid, m, address, host, type(message)))
        if len(message.original) > 1024*1024:
            raise SMTPError(523)
        
        if not message.base.parts:
            body = message.body()
        else:
            body = None
            for part in message.walk():
                if (not body) and ('text/plain' in part.content_encoding['Content-Type']):
                    body = part.body
                elif (not body) and ('html' in part.content_encoding['Content-Type']):
                    body = whitewash(part.body)
            if not body:
                body = message.body()
        
        m.thread.add_message(user=m.receiver, text=unicode(body), reply_to=m)
        # d = Message(
        #     sender=m.receiver,
        #     receiver=m.sender,
        #     reply_to=m, 
        #     thread=m.thread, 
        #     text=unicode(body),
        #     smtp_delivery_state='new',
        # )
        # d.save()
    elif message.Peer[0] in settings.ALLOWED_RELAY_HOSTS:
        logging.info('RELAYING %s %s %s' % (message, address, host))
        relay.deliver(message)
    else:
        raise SMTPError(571)

