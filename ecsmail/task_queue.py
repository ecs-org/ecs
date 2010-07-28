from celery.decorators import task

@task()
def queued_mail_send(message, To, From, through_receiver=False):
    from django.conf import settings
    from lamson.server import Relay
    if through_receiver:
        relay = Relay(host=settings.LAMSON_RECEIVER_CONFIG['host'],
            port=settings.LAMSON_RECEIVER_CONFIG['port'])
    else:
        relay = Relay(host=settings.LAMSON_RELAY_CONFIG['host'],
            port=settings.LAMSON_RELAY_CONFIG['port'])
    relay.deliver(message, To, From)
