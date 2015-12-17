# -*- coding: utf-8 -*-
import json

from django.test.utils import override_settings

from ecs.utils.testcases import LoginTestCase


class DecoratorApiTest(LoginTestCase):
    '''Tests for the Docstash
    
    Test for sending and receiving data from and to the docstash.
    '''

    @override_settings(ROOT_URLCONF='ecs.docstash.tests.urls')
    def test_simple_post(self):
        '''Tests if data can be submitted to the docstash, and read again.
        Posted data is compared against data read from the docstash.
        '''

        base_url = '/simple_post/'
        test_post_data = {'foo': 'bar'}
        response = self.client.post(base_url)
        self.assertEqual(response.status_code, 302)
        key_url = response['Location']
        self.assertTrue(base_url in key_url)
        key = key_url.rsplit('/', 2)[-2]

        # post test data
        response = self.client.post(key_url, test_post_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, test_post_data)

        # get test data
        response = self.client.get(key_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, test_post_data)

        # post test data again
        test_post_data = {'baz': '42'}
        response = self.client.post(key_url, test_post_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, test_post_data)
