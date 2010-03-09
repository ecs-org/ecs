# -*- coding: utf-8 -*-
#
# (c) 2010 Medizinische Universität Wien
#

"""
Unittests for docstash
"""

from django.test import TestCase
from django.test.client import Client
from django.utils.simplejson import loads

class TestDocstashAPI:
    def setUp(self):
        self.c = Client()

    def test_create(self):
        response = self.c.post("/docstash/create", dict(name="name", form="form"))
        data = loads(response.content)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[1] == 1
        assert isinstance(data[0], basestring)
