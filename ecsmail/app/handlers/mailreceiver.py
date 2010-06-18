import logging
import re
from lamson.routing import route, route_like, stateless
from lamson import view, queue
from lamson.bounce import bounce_to
from lamson.server import SMTPError

from django.conf import settings
from ecs.messages.models import Message

from ecs.ecsmail.config import settings as lamsettings
from ecs.ecsmail.persil import whitewash

@route(".+")
def IGNORE_BOUNCE(message):
    print "REALLY HANDLING BOUNCE", message
    bounces = queue.Queue(lamsettings.BOUNCES)
    bounces.push(message)
    return START

@route("(address)@(host)", address=".+")
@bounce_to(soft=IGNORE_BOUNCE, hard=IGNORE_BOUNCE)
@stateless
def START(message, address=None, host=None):
    from ecs.ecsmail.config.settings import relay
        
    muuid = None
    if host == settings.DEFAULT_FROM_DOMAIN: # we acccept mail for this address
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
        if len(m.original) > 1024*1024:
            raise SMTPError(523)
        
        if not m.base.parts:
            body = m.body()
        else:
            body = None
            for part in m.walk():
                if (not body) and (part.subtype == 'plain'):
                    body = part.body
                elif (not body) and ('html' in part.subtype):
                    body = whitewash(part.body)
            if not body:
                body = m.body()

        d = Message(
            sender=m.receiver,
            receiver=m.sender,
            reply_to=m, 
            thread=m.thread, 
            text=unicode(body),
            smtp_delivery_state='new',
        )
        d.save()
    elif message.Peer[0] == '127.0.0.1':
        logging.info('RELAYING %s %s %s' % (message, address, host))
        relay.deliver(message)
    else:
        raise SMTPError(571)

