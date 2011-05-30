# -*- coding: utf-8 -*-

from uuid import uuid4
from time import time

from ecs.utils.testcases import EcsTestCase
from ecs.mediaserver.client import authUrl

class authUrlTest(EcsTestCase):
    
    baseurl =  "http://void"
    bucket = "/"
    keyid = "CyKK3sUdWCVxOMIvoyW8"
    keysecret = "7GEVGvImpCIxidINqA3MEOU5zBJDeCf"
        
    def testConsistency(self):
        uuid = uuid4()
        hasExpired = int(time())
        willExpire = hasExpired + 60
        
        authurl = authUrl(self.keyid, self.keysecret)
        url = authurl.grant(self.baseurl, self.bucket, uuid.get_hex(), self.keyid, willExpire)
        bucket, objectid, keyid, expires, signature = authurl.parse(url)
        self.assertEqual(authurl.verify_parsed(bucket, objectid, keyid, expires, signature), True)
        self.assertEqual(authurl.verify(url), True)
        
        url = authurl.grant(self.baseurl, self.bucket, uuid.get_hex(), self.keyid, hasExpired)
        bucket, objectid, keyid, expires, signature = authurl.parse(url)
        self.assertEqual(authurl.verify_parsed(bucket, objectid, keyid, expires, signature), False)
        self.assertEqual(authurl.verify(url), False)
        