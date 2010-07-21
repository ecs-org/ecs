# from ecs.ecsmail.config import settings
from django.conf import settings

from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver
from lamson import view, queue
import logging
import logging.config
import os
import os.path
os.environ['LAMSON_LOADED'] = 'True'

# import jinja2
# logging.config.fileConfig("config/logging.conf")

# the relay host to actually send the final message to
relay = Relay(host=settings.RELAY_CONFIG['host'], 
                       port=settings.RELAY_CONFIG['port']) # , debug=1

# where to listen for incoming messages
receiver = SMTPReceiver(settings.RECEIVER_CONFIG['host'],
                                 settings.RECEIVER_CONFIG['port'])

Router.defaults(**settings.ROUTER_DEFAULTS)
Router.load(settings.HANDLERS)
Router.RELOAD=True
Router.UNDELIVERABLE_QUEUE=queue.Queue(settings.UNDELIVERABLE_QUEUE)

# view.LOADER = jinja2.Environment(
#     loader=jinja2.PackageLoader(settings.template_config['dir'], 
#                                 settings.template_config['module']))

