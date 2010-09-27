'''
Created on 26.09.2010

@author: felix
'''

import sys
import random
import subprocess, atexit
import os.path

if not os.path.exists('ecsmail.lock'):
    _port = random.randint(30000, 60000)
    LAMSON_RELAY_CONFIG = {'host': '127.0.0.1', 'port': _port} # smartmx dummy
    EMAIL_HOST = LAMSON_RELAY_CONFIG['host']
    EMAIL_PORT = LAMSON_RELAY_CONFIG['port']
    
    with open('ecsmail.lock', 'w'):
        # xxx: sys.executable should work in most environments (if you want python, you probably get python with it)
        cmd = [os.path.normpath(sys.executable), sys.argv[0], 'ecsmail', 'log', str(_port)] 
        # let the log server listen on smartmx dummy
        print ' '.join(cmd)
        ecsmail = subprocess.Popen(cmd)
        def cleanup():
            ecsmail.terminate()
            os.remove('ecsmail.lock')
        atexit.register(cleanup)
        
