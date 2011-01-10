import random

from windmill.authoring.djangotest import start_test_server as start_orig
from windmill.authoring import djangotest

def start_test_server(self, *args, **kwargs):
    port = random.randint(16000, 65535)
    print 'Starting Test server on port {0}'.format(port)
    return start_orig(self, port=port, *args, **kwargs)


djangotest.start_test_server = start_test_server


from windmill.management.commands.test_windmill import Command


