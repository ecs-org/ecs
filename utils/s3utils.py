'''
Created on Sep 19, 2010

@author: elchaschab
'''

from ecs.utils.django_signed.signed import base64_hmac
from django.conf import settings
from urlparse import urlparse, parse_qs

def createExpiringUrl(baseurl, bucket, objectid, keyId, expires):
    signature = _createSignatur(bucket, objectid, keyId, expires);
    url = "%s%s%s?AWSAccessKeyId=%s&amp;Expires=%s&amp;Signature=%s" % (baseurl, bucket, objectid, keyId, expires, signature) 
    auth_header = "Authorization: AWS %s:%s" (keyId, signature)
    
    return url, auth_header

def _createSignatur(bucket, objectid, keyId, expires):
    secretKey = settings.S3_SECRET_KEYS[keyId]
    if not secretKey:
        raise KeyError("Unknown s3 key: " + keyId)

    signme = "GET\n\n\n%s\n%s%s" % (expires, bucket, objectid);
    return base64_hmac(signme, secretKey);
    
def verifyExpiringUrl(bucket, objectid, keyId, expires, signature):
    expected_signature = _createSignatur(bucket, objectid, keyId, expires);
    
    return expected_signature == signature

def parseS3UrlFeatures(urlstring):
    parsedurl = urlparse(urlstring);
    query_dict = parse_qs(parsedurl.query)
    tail, sep ,head = parsedurl.path.rpartition("/");
    
    bucket = tail + sep
    objectid = head
    keyId = query_dict["AWSAccessKeyId"]
    expires = query_dict["Expires"]
    signature = query_dict["Signature"]
    
    return (bucket, objectid, keyId, expires, signature)