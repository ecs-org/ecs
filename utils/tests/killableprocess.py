import subprocess

from django.test import TestCase
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse

from ecs.utils import killableprocess
from ecs.utils import forceauth
import os, sys

SLEEPS_ALOT= [os.path.normpath(sys.executable), '-c', 'from time import sleep; sleep(100)']

@forceauth.exempt
def timeout_view(request):
    popen = killableprocess.Popen(args=SLEEPS_ALOT)
    retcode = popen.wait(timeout=2)
    return HttpResponse(str(retcode))

urlpatterns = patterns('',
    url(r'^test/$', timeout_view),
)

class KillableProcessTest(TestCase):
    '''Tests for the killableprocesses module
    
    Tests for killing a process.
    '''
    
    urls = 'ecs.utils.tests.killableprocess'

    def test_timeout(self):
        '''Tests if a process is killed after specified timeout.
        '''
        
        popen = killableprocess.Popen(args=SLEEPS_ALOT)
        retcode = popen.wait(timeout=2)
        self.assertNotEquals(retcode, 0)
        
    def test_client(self):
        '''Tests if the test url is reachable via the test client.
        '''
        
        response = self.client.get('/test/')
        print response.status_code
        self.failUnlessEqual(response.status_code, 200)
        
