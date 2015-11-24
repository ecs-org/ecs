# -*- coding: utf-8 -*-

import time, logging
from tempfile import NamedTemporaryFile
from urllib import urlencode
from urlparse import urlparse, parse_qs

from django.conf import settings

from ecs.utils.django_signed.signed import base64_hmac
from ecs.utils.pdfutils import pdf_barcodestamp

from ecs.mediaserver.storagevault import getVault
from ecs.mediaserver.diskbuckets import DiskBuckets


class MediaProvider:
    ''' Media loading from vault, caching, rendering and retrieval Provider.
    
    Implements 2 way caching, re/rendering service for application/pdf
    
    :note: uses celery for tasks.do_aging to perform asynchronous aging.
    :raise KeyError: get_blob, raise KeyError in case getting of data went wrong
    '''

    def __init__(self, allow_mkrootdir=False):
        self.doc_diskcache = DiskBuckets(settings.MS_SERVER ["doc_diskcache"],
            max_size= settings.MS_SERVER ["doc_diskcache_maxsize"], allow_mkrootdir= allow_mkrootdir)
        self.vault = getVault()
        
    def _cache_blob(self, identifier, filelike):
        ''' create/udpate a blob into the diskcache directly '''
        self.doc_diskcache.create_or_update(identifier, filelike)

    def add_blob(self, identifier, filelike): 
        ''' add (create or fail) a blob in the storage vault
        :raise KeyError: if store to vault fails
        '''
        logger = logging.getLogger()
        logger.debug("add_blob (%s), filelike is %s", identifier, filelike)
        try:
            self.vault.add(identifier, filelike)
        except Exception as e:
            raise KeyError("adding to storage vault resulted in an exception: {0}".format(e))

    def get_blob(self, identifier, try_diskcache=True, try_vault=True):
        '''get a blob (unidentified media data) either from caches, or from storage vault
    
        :raise KeyError: if reading the data of the identifier went wrong 
        '''
        filelike=None
                
        if try_diskcache:
            filelike = self.doc_diskcache.get_or_None(identifier, touch_accesstime=True)
        
        if not filelike and try_vault and identifier:
            try:
                filelike = self.vault.get(identifier)
                self.doc_diskcache.create_or_update(identifier, filelike)
            except Exception as exceptobj:
                raise KeyError, "could not load blob with identifier %s, exception was %r" % (identifier, exceptobj)
            finally:
                self.vault.decommission(filelike)    
            
            filelike = self.doc_diskcache.get_or_None(identifier)
        
        if not filelike:
            raise KeyError, "could not load blob with identifier %s" % (identifier)

        return filelike

    def get_branded(self, identifier, mimetype='application/pdf', branding=None):
        ''' get a branded blob (identified by mimetype) either from caches, or from storage vault and re-render branding
    
        :raise KeyError: if reading the data of the identifier went wrong 
        '''
        f = None
        
        if branding is None:
            f = self.get_blob(identifier)     
        else:    
            try: # look if identifier+identifier filename is already there (file with stamp)
                f = self.get_blob(identifier+identifier, try_vault=False)            
            except KeyError:
                try:
                    # regenerate branded pdf and cache result before delivering
                    inputpdf = self.get_blob(identifier)
                    
                    with NamedTemporaryFile(suffix='.pdf') as outputpdf:
                        pdf_barcodestamp(inputpdf, outputpdf, identifier)
                        outputpdf.seek(0)
                        self._cache_blob(identifier+identifier, outputpdf)
                except (EnvironmentError, KeyError) as e:
                    raise KeyError(e)

                f = self.get_blob(identifier+identifier, try_vault=False)        
                
        return f


class AuthUrl:
    def __init__(self, KeyId, KeySecret):
        self.keystore = {KeyId: KeySecret}    
    
    def _create_signature(self, bucket, objectid, keyId, expires):
        secretKey = self.keystore [keyId]
        signme = "GET\n\n\n%s\n%s%s" % (expires, bucket, objectid)
        return base64_hmac(signme, secretKey)

    def parse(self, urlstring):
        parsedurl = urlparse(urlstring)
        query_dict = parse_qs(parsedurl.query)
        tail, sep, head = parsedurl.path.rpartition("/")
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
            return (int(expires) > int(time.time()) and expected_signature == signature)
    
    def verify(self, urlstring):
        bucket, objectid, keyId, expires, signature = self.parse(urlstring)
        return self.verify_parsed(bucket, objectid, keyId, expires, signature)
