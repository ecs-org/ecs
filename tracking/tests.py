# -*- coding: utf-8 -*-
import time

from ecs.utils.testcases import EcsTestCase
from ecs.tracking import tasks
from ecs.tracking.models import Request
from ecs.users.utils import get_user


class CleanupTest(EcsTestCase):
    ''' '''
    
    def setUp(self):
        super(CleanupTest, self).setUp()
        self._original_max_requests = tasks.MAX_REQUESTS_PER_USER
        tasks.MAX_REQUESTS_PER_USER = 3
        
    def tearDown(self):
        super(CleanupTest, self).tearDown()
        tasks.MAX_REQUESTS_PER_USER = self._original_max_requests
    
    def test_cleanup(self):
        '''Tests that tracking the number of requests per user works.'''
        
        users = ('alice@example.com', 'bob@example.com',)
        N = tasks.MAX_REQUESTS_PER_USER + 2
        for user in users:
            with self.login(user, 'password'):
                for i in xrange(N):
                    response = self.client.get('/dashboard/')
                    time.sleep(2) # make shure we get different timestamps
        self.assertEqual(Request.objects.count(), N * len(users))
        
        tasks.cleanup_requests()
        
        for user in users:
            self.assertEqual(get_user(user).requests.count(), tasks.MAX_REQUESTS_PER_USER)

        
        
