import os
import logging
import logging.config

from django.conf import settings

from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver
from lamson import queue

import ecs.ecsmail.monkey

relay = Relay(host= settings.EMAIL_HOST, port= settings.EMAIL_PORT, starttls= settings.EMAIL_USE_TLS,
    username = settings.EMAIL_HOST_USER, password= settings.EMAIL_HOST_PASSWORD)
# Monkey Patch deliver so it will use ecsmail settings (and django backends)
relay.deliver = ecs.ecsmail.monkey.deliver 

receiver = SMTPReceiver(settings.ECSMAIL ['listen'], settings.ECSMAIL ['port'])

Router.defaults({'host': '.+'})
Router.load(settings.ECSMAIL ['handlers'])
Router.RELOAD = False
Router.UNDELIVERABLE_QUEUE = queue.Queue(os.path.join(settings.ECSMAIL ['queue_dir'], "undeliverable"))
