import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Starts ecsmail frontend server or a dummy logging backend server'
    args = '<server [logfile] | logging [port]>'

    def handle(self, *args, **options):
        from ecs.ecsmail.logconf import setLogging
        
        if len(args) < 1:
            print("Usage: ecsmail ", self.args)
            return 

        elif args[0] == 'server':
            logfile = args[1] if len(args) >= 2 else None
            setLogging(logfile)

            from ecs.ecsmail import lamson_settings
            import asyncore
            print("starting ecsmail server, Listen: %s:%s, Relay: %s" % 
                (lamson_settings.receiver.host, lamson_settings.receiver.port, str(lamson_settings.relay)))
            asyncore.loop(timeout=0.1, use_poll=True)
            
        elif args[0] == 'logging':
            setLogging()

            from lamson import utils
            port = int(args[1]) if len(args) >= 2 else 8825
            listen = '0.0.0.0'
            lamson_settings = utils.make_fake_settings(listen, port)
            print("starting ecsmail logging server, Listen: %s:%i" % (listen, port))
            import asyncore
            asyncore.loop(timeout=0.1, use_poll=True)
            
        else:
            print("Usage: ecsmail", self.args)
            return 
