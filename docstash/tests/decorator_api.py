# -*- coding: utf-8 -*-
from django.test import TestCase
from django.utils import simplejson

from ecs.docstash.models import DocStash

class DecoratorApiTest(TestCase):
    urls = 'ecs.docstash.tests.urls'
    
    def _check_version_cookie(self, key, version):
        self.failUnlessEqual(int(self.client.cookies['docstash_%s' % key].value), version)

    def test_simple_post(self):
        base_url = '/simple_post/'
        test_data = {'foo': 'bar'}
        response = self.client.post(base_url, test_data)
        self.failUnlessEqual(response.status_code, 302)
        key_url = response['Location']
        self.failUnless(base_url in key_url)
        key = key_url.rsplit('/', 2)[-2]
        self._check_version_cookie(key, -1)
        
        # post test data
        response = self.client.post(key_url, test_data)
        self.failUnlessEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.failUnlessEqual(data, test_data)
        self._check_version_cookie(key, 0)
        
        # get test data
        response = self.client.get(key_url)
        self.failUnlessEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.failUnlessEqual(data, test_data)
        self._check_version_cookie(key, 0)
        
        # post test data again
        test_data = {'baz': '42'}
        response = self.client.post(key_url, test_data)
        self.failUnlessEqual(response.status_code, 200)
        data = simplejson.loads(response.content)
        self.failUnlessEqual(data, test_data)
        self._check_version_cookie(key, 1)


        
