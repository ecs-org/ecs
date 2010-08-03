from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import ecs
import sys
import os
import signal
from lamson import utils

class Command(BaseCommand):
    help = 'Starts ecsmail frontend server and/or logging backend server'
    args = '<server|log [port]>'

    def handle(self, *args, **options):
        import ecs.ecsmail.logconf
        os.chdir(os.path.join(os.path.dirname(ecs.__file__), 'ecsmail'))
        
        if len(args) < 1:
            print("Usage: ecsmail ", self.args)
            return 
        elif args[0] == 'server':
            from lamson.server import SMTPReceiver
            from ecs.ecsmail.config import boot as lamsettings
            # inject receiver into lamsettings
            lamsettings.receiver = SMTPReceiver(settings.LAMSON_RECEIVER_CONFIG['host'], 
                settings.LAMSON_RECEIVER_CONFIG['port'])

            import asyncore
            print("starting ecsmail server, Listen: %s:%s, Relay:  %s" % (lamsettings.receiver.host, lamsettings.receiver.port, str(lamsettings.relay)))
            asyncore.loop(timeout=0.1, use_poll=True)

        elif args[0] == 'log':
            if len(args) == 2:
                port= int(args[1])
            else:
                port = settings.LAMSON_RELAY_CONFIG['port']

            host = settings.LAMSON_RELAY_CONFIG['host']
            lamsettings = utils.make_fake_settings(host, port)
            print("starting ecsmail testing log server, Listen: %s:%i" % (host, port))
            import asyncore
            asyncore.loop(timeout=0.1, use_poll=True)
        else:
            print("Usage: ecsmail", self.args)
            return 
            