import subprocess

from django.test import TestCase
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse

from ecs.utils import killableprocess

def timeout_view(request):
    popen = killableprocess.Popen('top', stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    retcode = popen.wait(timeout=1)
    return HttpResponse(popen.stdout.read())

urlpatterns = patterns('',
    url(r'^test/$', timeout_view),
)

class KillableProcessTest(TestCase):
    urls = 'ecs.utils.tests.killableprocess'

    def test_timeout(self):
        popen = killableprocess.Popen('top')
        retcode = popen.wait(timeout=1)
        self.failIfEqual(retcode, 0)
        
    def test_client(self):
        response = self.client.get('/test/')
        self.failUnlessEqual(response.status_code, 200)
        
