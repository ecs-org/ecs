# -*- coding: utf-8 -*-

from time import time
from urlparse import urlparse, parse_qs
from ecs.utils.django_signed.signed import base64_hmac

class S3url(object):
    def __init__(self, KeyId, KeySecret):
        self.keystore = {KeyId: KeySecret}
        
    def createUrl(self, baseurl, bucket, objectid, keyId, expires):
        signature = self._createSignature(bucket, objectid, keyId, expires)
        url = "%s%s%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s" % (baseurl, bucket, objectid, keyId, expires, signature) 
        #auth_header = "Authorization: AWS %s:%s" % (keyId, signature)
        return url
    
    def _createSignature(self, bucket, objectid, keyId, expires):
        secretKey = self.keystore [keyId]
        signme = "GET\n\n\n%s\n%s%s" % (expires, bucket, objectid)
        return base64_hmac(signme, secretKey)
        
    def verifyUrl(self, bucket, objectid, keyId, expires, signature):
        if keyId not in self.keystore:
            return False
        else:
            expected_signature = self._createSignature(bucket, objectid, keyId, expires)
            return (int(expires) > int(time()) and expected_signature == signature)
    
    def verifyUrlString(self, urlstring):
        bucket, objectid, keyId, expires, signature = self.parseS3UrlFeatures(urlstring)
        return self.verifyUrl(bucket, objectid, keyId, expires, signature)
    
    def parseS3UrlFeatures(self, urlstring):
        parsedurl = urlparse(urlstring)
        query_dict = parse_qs(parsedurl.query)
        tail, sep ,head = parsedurl.path.rpartition("/")
        bucket = tail + sep
        objectid = head
        keyId = query_dict["AWSAccessKeyId"].pop() if "AWSAccessKeyId" in query_dict else None
        expires = query_dict["Expires"].pop() if "Expires" in query_dict else None
        signature = query_dict["Signature"].pop() if "Signature" in query_dict else None
        return (bucket, objectid, keyId, expires, signature)
