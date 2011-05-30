# -*- coding: utf-8 -*-
from time import time
from urllib2 import urlopen
from urlparse import urlparse, parse_qs
from urllib import urlencode

from django.conf import settings

from ecs.utils.django_signed.signed import base64_hmac


def add_to_storagevault(uuid, filelike): 
    ''' add (create or fail) a blob in the storage vault
    '''
    from ecs.mediaserver.utils import MediaProvider
    m = MediaProvider()
    m.add_blob(uuid, filelike)


def prime_mediaserver(uuid, mimetype='application/pdf', personalization=None, brand=False):
    ''' pokes mediaserver to ready cache for media with uuid
    @return: tuple: Success:True/False,Response:Text
    '''   
    
    if settings.CELERY_ALWAYS_EAGER or settings.MS_CLIENT.get('same_host_as_server', False):
        from ecs.mediaserver.utils import MediaProvider
        m = MediaProvider()
        wait = True if settings.CELERY_ALWAYS_EAGER else False
        result, identifier, response = m.prime_blob(uuid, mimetype, wait=wait)
        return result, response
    else:
        #TODO: using urlopen and lot of data over the internet might go wrong: Add resilience
        objid_parts = ['prepare', uuid, mimetype]
        objid = '/'.join(objid_parts) + '/'
    
        key_id = settings.MS_CLIENT ["key_id"]
        expires = int(time()) + settings.MS_SHARED['url_expiration_sec']
    
        authurl = authUrl(key_id, settings.MS_CLIENT['key_secret'])
        url= authurl.grant(settings.MS_CLIENT['server'], settings.MS_CLIENT['bucket'], objid, key_id, expires)

        f = urlopen(url)
        response = f.read()
        f.close()
        if not response == 'ok':
            return False, response
        

def download_from_mediaserver(uuid, filename, personalization=None, brand=False):
    ''' returns blob from mediaserver as data; seldom usage.
    @see: generate_media_url() if you just want to pass access safely through the media server temporary urls
    @note: you may want this if you need the data for further processing, eg. export submission
    '''
    if settings.MS_CLIENT.get('same_host_as_server', False):
        from ecs.mediaserver.utils import MediaProvider
        return MediaProvider().get_blob(uuid)
    else:
        # TODO using urlopen and lot of data over the internet might go wrong: Add resilience
        f = urlopen(generate_media_url(uuid, filename, personalization=personalization, brand=brand))
        return f


def generate_media_url(uuid, filename, mimetype='application/pdf', personalization=None, brand=False):
    ''' @return:  url that will allow a user to download this blob by using this url for a specific time period
    '''
    objid_parts = ['download', uuid, mimetype]
    if personalization:
        objid_parts += ['brand', personalization]
    elif brand:
        objid_parts += ['brand', "True"]
    objid_parts.append(filename)

    objid = '/'.join(objid_parts) + '/'

    key_id = settings.MS_CLIENT ["key_id"]
    expires = int(time()) + settings.MS_SHARED['url_expiration_sec']

    authurl = authUrl(key_id, settings.MS_CLIENT['key_secret'])
    return authurl.grant(settings.MS_CLIENT['server'], settings.MS_CLIENT['bucket'], objid, key_id, expires)


def generate_pages_urllist(uuid, pages):
    ''' returns a list of ('description', 'access-url', 'page', 'tx', 'ty', 'width', 'height')
    for every supported rendersize options for every page of the document with uuid
    '''
    tiles = settings.MS_SHARED ["tiles"]
    width = settings.MS_SHARED ["resolutions"]
    aspect_ratio = settings.MS_SHARED ["aspect_ratio"]
    expiration_sec = settings.MS_SHARED ["url_expiration_sec"]
    
    baseurl = settings.MS_CLIENT ["server"]
    bucket = settings.MS_CLIENT ["bucket"]
    key_id = settings.MS_CLIENT ["key_id"]
    key_secret = settings.MS_CLIENT ["key_secret"]
    docshotData = [];
    
    for t in tiles:
        for w in width:
            tilepages = pages / (t*t)
            if pages % (t*t) > 0: tilepages += 1
             
            for pagenum in range(1, tilepages+1):
                objectid = "%s/%dx%d/%d/%d/" % (uuid, t, t, w, pagenum)
                expires = int(time()) + expiration_sec
                h =  w * aspect_ratio
                docshotData.append({
                    'description': "Page: %d, Tiles: %dx%d, Width: %dpx" % (pagenum, t, t, w),
                    'url': authUrl(key_id, key_secret).grant(baseurl, bucket, objectid, key_id, expires), 
                    'page': pagenum, 
                    'tx': t,
                    'ty': t,
                    'width': w, 
                    'height': h,
                })
                pagenum += 1
    return docshotData


class authUrl(object):
    def __init__(self, KeyId, KeySecret):
        self.keystore = {KeyId: KeySecret}    
    
    def _create_signature(self, bucket, objectid, keyId, expires):
        secretKey = self.keystore [keyId]
        signme = "GET\n\n\n%s\n%s%s" % (expires, bucket, objectid)
        return base64_hmac(signme, secretKey)

    def parse(self, urlstring):
        parsedurl = urlparse(urlstring)
        query_dict = parse_qs(parsedurl.query)
        tail, sep ,head = parsedurl.path.rpartition("/")
        bucket = tail + sep
        objectid = head
        keyId = query_dict["AWSAccessKeyId"].pop() if "AWSAccessKeyId" in query_dict else None
        expires = query_dict["Expires"].pop() if "Expires" in query_dict else None
        signature = query_dict["Signature"].pop() if "Signature" in query_dict else None
        return (bucket, objectid, keyId, expires, signature)
    
    def grant(self, baseurl, bucket, objectid, keyId, expires):
        signature = self._create_signature(bucket, objectid, keyId, expires)
        qd = {
            'AWSAccessKeyId': keyId,
            'Expires': expires,
            'Signature': signature,
        }
        url = '{0}{1}{2}?{3}'.format(baseurl, bucket, objectid, urlencode(qd)) 
        #auth_header = "Authorization: AWS %s:%s" % (keyId, signature)
        return url
        
    def verify_parsed(self, bucket, objectid, keyId, expires, signature):
        if keyId not in self.keystore:
            return False
        else:
            expected_signature = self._create_signature(bucket, objectid, keyId, expires)
            return (int(expires) > int(time()) and expected_signature == signature)
    
    def verify(self, urlstring):
        bucket, objectid, keyId, expires, signature = self.parse(urlstring)
        return self.verify_parsed(bucket, objectid, keyId, expires, signature)
    
