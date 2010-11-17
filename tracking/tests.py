import time
from ecs.utils.testcases import EcsTestCase
from django.contrib.auth.models import User
from ecs.tracking import tasks
from ecs.tracking.models import Request


class CleanupTest(EcsTestCase):
    def setUp(self):
        super(CleanupTest, self).setUp()
        self._original_max_requests = tasks.MAX_REQUESTS_PER_USER
        tasks.MAX_REQUESTS_PER_USER = 3
        
    def tearDown(self):
        super(CleanupTest, self).tearDown()
        tasks.MAX_REQUESTS_PER_USER = self._original_max_requests
    
    def test_cleanup(self):
        usernames = ('alice', 'bob')
        N = tasks.MAX_REQUESTS_PER_USER + 2
        for username in usernames:
            with self.login(username, 'password'):
                for i in xrange(N):
                    response = self.client.get('/dashboard/')
                    time.sleep(2) # make shure we get different timestamps
        self.assertEqual(Request.objects.count(), N * len(usernames))
        
        tasks.cleanup_requests()
        
        for username in usernames:
            self.assertEqual(User.objects.get(username=username).requests.count(), tasks.MAX_REQUESTS_PER_USER)

        
        