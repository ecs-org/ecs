import logging
import re
from lamson.routing import route, route_like, stateless
from lamson import view, queue
from lamson.bounce import bounce_to
from lamson.server import SMTPError

from django.conf import settings
from ecs.communication.models import Message
from ecs.ecsmail.persil import whitewash

@route(".+")
def IGNORE_BOUNCE(message):
    print "JUST A SOFT BOUNCE", message
    bounces = queue.Queue(settings.LAMSON_BOUNCES_QUEUE)
    bounces.push(message)
    return START

@route(".+")
def NOTIFY_BOUNCE(message):
    print "REALLY HANDLING BOUNCE", message
    bounces = queue.Queue(settings.LAMSON_BOUNCES_QUEUE)
    bounces.push(message)
    return START

@route("(address)@(host)", address=".+")
@bounce_to(soft=IGNORE_BOUNCE, hard=NOTIFY_BOUNCE)
@stateless
def START(message, address=None, host=None):
    from ecs.ecsmail.config.boot import relay
        
    muuid = None
    if host == settings.FROM_DOMAIN: # we acccept mail for this address
        logging.info('FROM DOMAIN: %s' % (address,))
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
            raise SMTPError(511) # Bad destination mailbox address
        
        logging.info('REPLY %s %s %s %s %s' % ( muuid, m, address, host, type(message)))
        if len(message.original) > 1024*1024:
            raise SMTPError(523) # 'Message length exceeds administrative limit.'
        
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

    elif message.Peer[0] in settings.LAMSON_ALLOWED_RELAY_HOSTS:
        logging.info('RELAYING %s %s %s' % (repr(message), address, host))
        relay.deliver(message)
    else:
        raise SMTPError(571) #Delivery not authorized, message refused

