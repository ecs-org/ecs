# -*- coding: utf-8 -*-
from django.utils import simplejson
from ecs.utils.testcases import LoginTestCase
from ecs.docstash.models import DocStash

class DecoratorApiTest(LoginTestCase):
    '''Tests for the Docstash
    
    Test for sending and receiving data from and to the docstash.
    '''
    
    urls = 'ecs.docstash.tests.urls'
    
    def test_simple_post(self):
        '''Tests if data can be submitted to the docstash, and read again.
        Posted data is compared against data read from the docstash.
        '''
        
        base_url = '/simple_post/'
        test_post_data = {'foo': 'bar'}
        response = self.client.post(base_url)
        self.failUnlessEqual(response.status_code, 302)
        key_url = response['Location']
        self.failUnless(base_url in key_url)
        key = key_url.rsplit('/', 2)[-2]
        
        # post test data
        response = self.client.post(key_url, test_post_data)
        self.failUnlessEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.failUnlessEqual(data, test_post_data)
        
        # get test data
        response = self.client.get(key_url)
        self.failUnlessEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.failUnlessEqual(data, test_post_data)
        
        # post test data again
        test_post_data = {'baz': '42'}
        response = self.client.post(key_url, test_post_data)
        self.failUnlessEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.failUnlessEqual(data, test_post_data)


        
