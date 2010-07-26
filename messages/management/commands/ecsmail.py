from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from ecs.messages.models import Message
from ecs.utils.datastructures import OrderedSet
from ecs.messages.mail import send_mail

import ecs
import sys
import os
import signal
from lamson import utils

class Command(BaseCommand):
    help = 'Starts ecsmail.'

    def handle(self, *args, **options):
        import ecs.ecsmail.logconf
        os.chdir(os.path.join(os.path.dirname(ecs.__file__), 'ecsmail'))
        
        if len(args) < 1:
            print 'usage: ecsmail <server|log [port]> '
            return 
        elif args[0] == 'server':
            # from ecs.ecsmail.config import settings as lamsettings
            from ecs.ecsmail.config import boot
            import asyncore
            asyncore.loop(timeout=0.1, use_poll=True)
        elif args[0] == 'log':
            if len(args) == 2:
                port= int(args[1])
            else:
                port = settings.ECSMAIL_LOGSERVER_PORT
            lamsettings = utils.make_fake_settings('127.0.0.1', port)
            print("lamson log on 127.0.0.1 port", port)
            import asyncore
            asyncore.loop(timeout=0.1, use_poll=True)
        else:
            print 'usage: ecsmail <server|log [host port]> '
            return 