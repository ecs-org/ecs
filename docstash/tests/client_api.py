# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
Unittests for docstash API
"""

from django.test import TestCase
from django.test.client import Client
from django.utils.simplejson import loads, dumps

class ClientApiTest(TestCase):
    def test_create(self):
        response = self.client.post("/docstash/create/test/")
        data = loads(response.content)
        assert isinstance(data, list)
        assert len(data) == 2
        assert isinstance(data[0], basestring)
        assert data[1] == -1

    def test_read(self):
        response = self.client.post("/docstash/create/test/")
        key, version = loads(response.content)
        response = self.client.get("/docstash/%s" % key)
        self.failUnlessEqual(response.status_code, 200)
        version, data = loads(response.content)
        self.failUnlessEqual(data, {})
        self.failUnlessEqual(version, -1)
        
    def test_post(self):
        test_data = dict(abc="def")
        response = self.client.post("/docstash/create/test/")
        key, version = loads(response.content)

        response = self.client.post("/docstash/%s/%s" % (key, version), dumps(test_data), "text/json")
        self.failUnlessEqual(response.status_code, 200)
        version, data = loads(response.content)
        self.failUnlessEqual(data, test_data)

        response = self.client.get("/docstash/%s" % key)
        version, data = loads(response.content)
        self.failUnlessEqual(data, test_data)

    def test_key_uniqueness_on_create(self):
        response = self.client.post("/docstash/create/test/")
        key, version = loads(response.content)
        response = self.client.post("/docstash/create/test/")
        key2, version2 = loads(response.content)
        self.failIfEqual(key, key2)

