import time

from django.conf import settings

from ecs.utils.testcases import EcsTestCase
from ecs.tracking import tasks
from ecs.tracking.models import Request
from ecs.users.utils import get_user


class CleanupTest(EcsTestCase):
    '''Tests for the tracking module
    
    Tests for consistency of the cleanup functionality of the tracking module.'''
    
    def setUp(self):
        super(CleanupTest, self).setUp()
        self.original_tracking_status = getattr(settings, 'ECS_TRACKING_ENABLED', False)
        settings.ECS_TRACKING_ENABLED = True
        self._original_max_requests = tasks.MAX_REQUESTS_PER_USER
        tasks.MAX_REQUESTS_PER_USER = 3
        
    def tearDown(self):
        super(CleanupTest, self).tearDown()
        tasks.MAX_REQUESTS_PER_USER = self._original_max_requests
        settings.ECS_TRACKING_ENABLED = self.original_tracking_status
    
    def test_cleanup(self):
        '''High level test for making sure that tracking
        the number of requests per user works and that after
        a periodic cleanup the number of requests per user does not
        exceed the maximally allowed number
        '''
        
        users = ('alice@example.com', 'bob@example.com',)
        N = tasks.MAX_REQUESTS_PER_USER + 2
        for user in users:
            with self.login(user, 'password'):
                for i in range(N):
                    response = self.client.get('/dashboard/')
                    time.sleep(2) # make shure we get different timestamps
        self.assertEqual(Request.objects.count(), N * len(users))
        
        tasks.cleanup_requests()
        
        for user in users:
            self.assertEqual(get_user(user).requests.count(), tasks.MAX_REQUESTS_PER_USER)

        
        
