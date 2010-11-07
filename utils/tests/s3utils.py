# -*- coding: utf-8 -*-

from ecs.utils.testcases import EcsTestCase
from ecs.utils.s3utils import S3url
from uuid import uuid4
from time import time

class S3UtilsTest(EcsTestCase):
    
    baseurl =  "http://void"
    bucket = "/"
    keyid = "CyKK3sUdWCVxOMIvoyW8"
    keysecret = "7GEVGvImpCIxidINqA3MEOU5zBJDeCf"
        
    def testConsistency(self):
        uuid = uuid4()
        hasExpired = int(time())
        willExpire = hasExpired + 60
        
        s3url = S3url(self.keyid, self.keysecret)
        url = s3url.createUrl(self.baseurl, self.bucket, uuid.get_hex(), self.keyid, willExpire)
        bucket, objectid, keyid, expires, signature = s3url.parseS3UrlFeatures(url)
        self.assertEqual(s3url.verifyUrl(bucket, objectid, keyid, expires, signature), True)
        self.assertEqual(s3url.verifyUrlString(url), True)
        
        url = s3url.createUrl(self.baseurl, self.bucket, uuid.get_hex(), self.keyid, hasExpired)
        bucket, objectid, keyid, expires, signature = s3url.parseS3UrlFeatures(url)
        self.assertEqual(s3url.verifyUrl(bucket, objectid, keyid, expires, signature), False)
        self.assertEqual(s3url.verifyUrlString(url), False)
        