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

    def test_read(self):
        response = self.c.post("/docstash/create", dict(name="name", form="form"))
        data = loads(response.content)
        response = self.c.get("/docstash/%s" % data[0])
        data = loads(response.content)
        print data
        assert isinstance(data, list)
        assert len(data) == 2
        assert int(data[0]) or True, "token needs to be something compatible with int. Really"
        assert data[1] == None

    def test_search(self):
        import time
        result_time = int(time.time())
        self.c.post("/docstash/create", dict(name="name", form="form"))
        self.c.post("/docstash/create", dict(name="name abc", form="form"))
        self.c.post("/docstash/create", dict(name="name def", form="form"))        
        response = self.c.get("/docstash/search", dict(name="abc", form="form"))
        data = loads(response.content)
        assert len(data) == 1
        assert isinstance(data[0], dict)
        assert sorted(data[0].keys()) == sorted(["name", "form", "modtime", "key"])
        assert data[0]["name"] == "name abc"
        assert abs(int(data[0]["modtime"]) - result_time) < 5 # 5 secs for that test? If that takes THAT long, you should upgrade your C64 for something that is at least 16bit.
        
    def tearDown(self):
        from ecs.docstash.models import DocStash
        for o in DocStash.objects.all():
            o.delete()          # leave an empty database.

    def test_post(self):
        response = self.c.post("/docstash/create", dict(name="name", form="form"))
        data = loads(response.content)
        key, token = data
        response = self.c.post("/docstash/%s/%s" % tuple(data), dumps(dict(abc="def")), "text/json")
        assert response.status_code == 200
        response = self.c.get("/docstash/%s" % key)
        data = loads(response.content)
        assert data[1] == dict(abc="def")

    def test_key_uniqueness_on_create(self):
        response = self.c.post("/docstash/create", dict(name="name", form="form"))
        data_0 = loads(response.content)
        response = self.c.post("/docstash/create", dict(name="name", form="form"))
        data_1 = loads(response.content)
        assert data_0[0] != data_1[0]
        assert data_0[1] < data_1[1]


        response = self.c.post("/docstash/create", dict(name="name", form="form"))
        data_0 = loads(response.content)
        
        
