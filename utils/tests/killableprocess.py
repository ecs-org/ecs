import subprocess

from django.test import TestCase
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse

from ecs.utils import killableprocess
from ecs.utils import forceauth

@forceauth.exempt
def timeout_view(request):
    popen = killableprocess.Popen('more', stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    retcode = popen.wait(timeout=1)
    return HttpResponse(retcode)

urlpatterns = patterns('',
    url(r'^test/$', timeout_view),
)

class KillableProcessTest(TestCase):
    urls = 'ecs.utils.tests.killableprocess'

    def test_timeout(self):
        popen = killableprocess.Popen('more')
        retcode = popen.wait(timeout=1)
        self.failIfEqual(retcode, 0)
        
    def test_client(self):
        response = self.client.get('/test/')
        self.failUnlessEqual(response.status_code, 200)
        
