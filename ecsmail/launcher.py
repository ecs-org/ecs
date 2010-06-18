import sys
import os
import logconf
from lamson import utils

def main():
    if len(sys.argv) <= 1:
        print 'usage: %s <server|log>' % (sys.argv[0])
        return
    elif sys.argv[1] == 'server':
        from ecs.ecsmail.config import settings
        from ecs.ecsmail.config import boot
    elif sys.argv[1] == 'log':
        settings = utils.make_fake_settings('127.0.0.1', 8825)

    print settings.relay
    settings.receiver.start()

if __name__ == '__main__':
    main()
