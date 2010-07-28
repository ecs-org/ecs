from django.conf import settings
from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver
from lamson import view, queue
import logging
import logging.config
import os
import os.path
os.environ['LAMSON_LOADED'] = 'True'

# the relay host to actually send the final message to
relay = Relay(host=settings.LAMSON_RELAY_CONFIG['host'], 
                       port=settings.LAMSON_RELAY_CONFIG['port']) # , debug=1

Router.defaults(**settings.LAMSON_ROUTER_DEFAULTS)
Router.load(settings.LAMSON_HANDLERS)
Router.RELOAD=True
Router.UNDELIVERABLE_QUEUE=queue.Queue(settings.LAMSON_UNDELIVERABLE_QUEUE)

