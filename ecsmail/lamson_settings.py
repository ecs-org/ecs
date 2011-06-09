from django.conf import settings

from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver
from lamson import queue


def monkey_patched_deliver(self, message, To=None, From=None):
    '''
    Takes a fully formed email message and delivers it to ecs.ecsmail.utils.deliver
    This gets monkey patched into lamson relay, to add support for standard ecs.ecsmail sending in case lamson
    somehow wants to send email (why ?, no idea, just as backup, in case lamson somehow wants to send mail)
    '''
    from ecs.ecsmail.utils import deliver as ecsmail_deliver
    
    recipient = To or message['To']
    sender = From or message['From']
    ecsmail_deliver(recipient, "[postmaster]", message, sender)


relay = Relay(host= settings.EMAIL_HOST, port= settings.EMAIL_PORT, starttls= settings.EMAIL_USE_TLS,
    username = settings.EMAIL_HOST_USER, password= settings.EMAIL_HOST_PASSWORD)
# Monkey Patch deliver so it will use ecsmail settings (and django backends)
relay.deliver = monkey_patched_deliver

receiver = SMTPReceiver(settings.ECSMAIL ['listen'], settings.ECSMAIL ['port'])

Router.defaults(host= '.+')
Router.load(settings.ECSMAIL ['handlers'])
Router.RELOAD = False
Router.UNDELIVERABLE_QUEUE = queue.Queue(settings.ECSMAIL ['queue_dir'])

