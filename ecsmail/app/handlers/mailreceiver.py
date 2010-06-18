import logging
import re
from lamson.routing import route, route_like, stateless
from lamson import view

from django.conf import settings
from ecs.messages.models import Message

@route("(address)@(host)", address=".+")
@stateless
def START(message, address=None, host=None):
    from ecs.ecsmail.config.settings import relay
    
    muuid = None
    if host == settings.DEFAULT_FROM_DOMAIN:
        logging.info('PREBLUB %s' % (address,))
        mat = re.match('ecs-([^@]+)', address)
        if mat:
            groups = mat.groups()
            if groups:
                muuid = groups[0]
    
    if muuid:
        m = Message.objects.get(uuid=muuid)
        logging.info('BLUB %s %s %s %s %s' % ( muuid, m, address, host, type(message)))
        d = Message(
            sender=m.receiver,
            receiver=m.sender,
            reply_to=m, 
            thread=m.thread, 
            text=unicode(message.body()),
            smtp_delivery_state='new',
        )
        d.save()
    else:
        logging.info('FROB %s %s %s' % (message, address, host))
        relay.deliver(message)