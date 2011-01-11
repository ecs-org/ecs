#   Copyright (c) 2008-2009 Mikeal Rogers <mikeal.rogers@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import random
import sys, os
from time import sleep
import types
import logging

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers import basehttp

from windmill.authoring import djangotest


class MyTestServerThread(djangotest.TestServerThread):

    def setUp(self):
        # Must do database stuff in this new thread if database in memory.
        from django.conf import settings
        create_db = False
        if hasattr(settings, 'DATABASES') and settings.DATABASES:
            # Django > 1.2
            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3' or \
                settings.DATABASES['default']['TEST_NAME']:
                create_db = True
        elif settings.DATABASE_ENGINE:
            # Django < 1.2
            if settings.DATABASE_ENGINE == 'sqlite3' and \
                (not settings.TEST_DATABASE_NAME or settings.TEST_DATABASE_NAME == ':memory:'):
                create_db = True
            
        if create_db:
            from django.db import connection
            db_name = connection.creation.create_test_db(0)
            # Import the fixture data into the test database.
            if hasattr(self, 'fixtures'):
                # We have to use this slightly awkward syntax due to the fact
                # that we're using *args and **kwargs together.
                call_command('loaddata', *self.fixtures, **{'verbosity': 1})

        # run migrations and bootstrap
        call_command('migrate')
        call_command('bootstrap')

        # reset translation cache
        from django.utils.translation import trans_real
        from django.utils.thread_support import currentThread
        from django.conf import settings
        import gettext

        gettext._translations = {}
        trans_real._translations = {}
        trans_real._default = None
        prev = trans_real._active.pop(currentThread(), None)
        trans_real.activate(settings.LANGUAGE_CODE)

    def run(self):
        """Sets up test server and loops over handling http requests."""
        try:
            handler = basehttp.AdminMediaHandler(WSGIHandler())
            httpd = None
            while httpd is None:
                try:
                    server_address = (self.address, self.port)
                    httpd = djangotest.StoppableWSGIServer(server_address, basehttp.WSGIRequestHandler)
                except basehttp.WSGIServerException, e:
                    if "Address already in use" in str(e):
                        self.port +=1
                    else:
                        raise e
            httpd.set_app(handler)
            self.started.set()
        except basehttp.WSGIServerException, e:
            self.error = e
            self.started.set()
            return

        # Loop until we get a stop event.
        while not self._stopevent.isSet():
            httpd.handle_request()
        httpd.server_close()


class ServerContainer(object):
    stop_test_server = djangotest.stop_test_server
    
    def start_test_server(self, address='127.0.0.1', port=None, fixtures=[]):
        if port is None:
            port = random.randint(16000, 65535)

        print 'Starting Test server on port {0}'.format(port)

        self.server_thread = MyTestServerThread(address, port, fixtures=fixtures)
        self.server_thread.setUp()
        self.server_thread.start()
        self.server_thread.started.wait()
        if self.server_thread.error:
            raise self.server_thread.error


def attempt_import(name, suffix):
        try:
            mod = __import__(name+'.'+suffix)
        except ImportError:
            mod = None
        if mod is not None:
            s = name.split('.')
            mod = __import__(s.pop(0))
            for x in s+[suffix]:
                mod = getattr(mod, x)
        return mod

class Command(BaseCommand):

    help = "Run windmill tests. Specify a browser, if one is not passed Firefox will be used"

    args = '<label label ...>'
    label = 'label'

    def handle(self, *labels, **options):

        from windmill.conf import global_settings
        from windmill.authoring.djangotest import WindmillDjangoUnitTest
        if 'ie' in labels:
            global_settings.START_IE = True
            sys.argv.remove('ie')
        elif 'safari' in labels:
            global_settings.START_SAFARI = True
            sys.argv.remove('safari')
        elif 'chrome' in labels:
            global_settings.START_CHROME = True
            sys.argv.remove('chrome')
        else:
            global_settings.START_FIREFOX = True
            if 'firefox' in labels:
                sys.argv.remove('firefox')

        if 'manage.py' in sys.argv:
            sys.argv.remove('manage.py')
        if 'test_windmill' in sys.argv:
            sys.argv.remove('test_windmill')
        server_container = ServerContainer()
        server_container.start_test_server()

        global_settings.TEST_URL = 'http://127.0.0.1:%d' % server_container.server_thread.port

        # import windmill
        # windmill.stdout, windmill.stdin = sys.stdout, sys.stdin
        from windmill.authoring import setup_module, teardown_module

        from django.conf import settings
        tests = []
        for name in settings.INSTALLED_APPS:
            for suffix in ['tests', 'wmtests', 'windmilltests']:
                x = attempt_import(name, suffix)
                if x is not None: tests.append((suffix,x,));

        wmtests = []
        for (ttype, mod,) in tests:
            if ttype == 'tests':
                for ucls in [getattr(mod, x) for x in dir(mod)
                             if ( type(getattr(mod, x, None)) in (types.ClassType,
                                                               types.TypeType) ) and
                             issubclass(getattr(mod, x), WindmillDjangoUnitTest)
                             ]:
                    wmtests.append(ucls.test_dir)

            else:
                if mod.__file__.endswith('__init__.py') or mod.__file__.endswith('__init__.pyc'):
                    wmtests.append(os.path.join(*os.path.split(os.path.abspath(mod.__file__))[:-1]))
                else:
                    wmtests.append(os.path.abspath(mod.__file__))

        if len(wmtests) is 0:
            print 'Sorry, no windmill tests found.'
        else:
            testtotals = {}
            x = logging.getLogger()
            x.setLevel(0)
            from windmill.dep import functest
            bin = functest.bin
            runner = functest.runner
            runner.CLIRunner.final = classmethod(lambda self, totals: testtotals.update(totals) )
            setup_module(tests[0][1])
            sys.argv = sys.argv + wmtests
            bin.cli()
            teardown_module(tests[0][1])
            if testtotals['fail'] is not 0:
                sleep(.5)
                sys.exit(1)
