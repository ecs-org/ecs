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
            print 'usage: ecsmail <server|log>'
            return
        elif args[0] == 'server':
            # from ecs.ecsmail.config import settings as lamsettings
            from ecs.ecsmail.config import boot
            import asyncore
            asyncore.loop(timeout=0.1, use_poll=True)
        elif args[0] == 'log':
            lamsettings = utils.make_fake_settings('127.0.0.1', settings.ECSMAIL_LOGSERVER_PORT)
            import asyncore
            asyncore.loop(timeout=0.1, use_poll=True)
