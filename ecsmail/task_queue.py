from celery.decorators import task
from django.conf import settings
import logging

@task()
def queued_mail_send(message, To, From, **kwargs):
    logger = queued_mail_send.get_logger(**kwargs)
    from django.conf import settings
    from lamson.server import Relay
    if not hasattr(settings,'LAMSON_SEND_THROUGH_RECEIVER'): 
        settings.LAMSON_SEND_THROUGH_RECEIVER = False
    if settings.LAMSON_SEND_THROUGH_RECEIVER == True:
        print"through receiver"
        relay = Relay(host=settings.LAMSON_RECEIVER_CONFIG['host'],
        port=settings.LAMSON_RECEIVER_CONFIG['port'])
    else:
        port = settings.LAMSON_RELAY_CONFIG['port']
        print"through relay", port
        relay = Relay(host=settings.LAMSON_RELAY_CONFIG['host'],
        port=port) #settings.LAMSON_RELAY_CONFIG['port'])

    logger.info("".join(("queued mail deliver using ", str(relay), ", from ", From, ", to ", To, ", msg ", repr(message))))
    relay.deliver(message, To, From)
    # FIXME needs errror handling and return value 
