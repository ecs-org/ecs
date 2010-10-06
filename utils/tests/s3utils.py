'''
Created on Sep 19, 2010

@author: elchaschab
'''
from django.test.testcases import TestCase
from ecs.utils.s3utils import createExpiringUrl, verifyExpiringUrl, parseS3UrlFeatures,\
    _createSignatur
from uuid import uuid4
from time import time

class S3UtilsTest(TestCase):
    baseurl =  "http://void"
    bucket = "/"
    keyid = "UnitTestKey"
    
    def testConsistency(self):
        uuid = uuid4()
        hasExpired = int(time())
        willExpire = hasExpired + 60
        
        url = createExpiringUrl(self.baseurl, self.bucket, uuid.get_hex(), self.keyid, willExpire)
        bucket, objectid, keyId, expires, signature = parseS3UrlFeatures(url)
        self.assertEqual(verifyExpiringUrl(bucket, objectid, keyId, expires, signature), True);
        
        url = createExpiringUrl(self.baseurl, self.bucket, uuid.get_hex(), self.keyid, hasExpired)
        bucket, objectid, keyId, expires, signature = parseS3UrlFeatures(url)
        self.assertEqual(verifyExpiringUrl(bucket, objectid, keyId, expires, signature), False);

        try:
            self.failIf(_createSignatur(self.bucket, uuid.get_hex(), "unknown key", willExpire))
        except KeyError:
            pass
        except:
            self.fail("Unknown key didn't cause KeyError")
