# -*- coding: utf-8 -*-

import os, time, getpass, logging

from tempfile import NamedTemporaryFile
from urllib import urlencode
from urlparse import urlparse, parse_qs

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from ecs.utils.django_signed.signed import base64_hmac
from ecs.utils.pathutils import tempfilecopy
from ecs.utils.pdfutils import pdf2pngs, pdf_barcodestamp

from ecs.mediaserver.storagevault import getVault, VaultError
from ecs.mediaserver.diskbuckets import DiskBuckets, BucketError  
from ecs.mediaserver.tasks import do_rendering


class MediaProvider:
    ''' Media loading from vault, caching, rendering and retrieval Provider.
    Implements 2 way caching, re/rendering service for application/pdf
    @note: uses celery for tasks.do_rendering for asynchronous rendering, tasks.do_aging for asynchronous aging.
    @raise KeyError: get_blob, get_page raise KeyError in case getting of data went wrong
    '''

    def __init__(self, allow_mkrootdir=False):
        self.render_memcache = VolatileCache()
        self.render_diskcache = DiskBuckets(settings.MS_SERVER ["render_diskcache"],
            max_size= settings.MS_SERVER ["render_diskcache_maxsize"], allow_mkrootdir= allow_mkrootdir)
        self.doc_diskcache = DiskBuckets(settings.MS_SERVER ["doc_diskcache"],
            max_size= settings.MS_SERVER ["doc_diskcache_maxsize"], allow_mkrootdir= allow_mkrootdir)
        self.vault = getVault()

    def _render_pages(self, identifier, filelike, private_workdir):
        ''' Yields page, imagedata for each tiles * resolution * pages set in settings.MS_SHARED
        @note: used by tasks.do_render to render actual data
        '''
        tiles = settings.MS_SHARED ["tiles"]
        resolutions = settings.MS_SHARED ["resolutions"]
        aspect_ratio = settings.MS_SHARED ["aspect_ratio"]
        dpi = settings.MS_SHARED ["dpi"]
        depth = settings.MS_SHARED ["depth"]   
        
        copied_file = False   
        if hasattr(filelike,"name"):
            tmp_sourcefilename = filelike.name
        elif hasattr(filelike, "read"):
            tmp_sourcefilename = tempfilecopy(filelike)
            copied_file = True
        
        try:   
            for t in tiles:
                for w in resolutions:
                    for page, data in pdf2pngs(identifier, tmp_sourcefilename, private_workdir, w, t, t, aspect_ratio, dpi, depth):
                        yield page, data
        finally:
            if copied_file:
                if os.path.exists(tmp_sourcefilename):
                    os.remove(tmp_sourcefilename)
        
    def _cache_blob(self, identifier, filelike):
        ''' create/udpate a blob into the diskcache directly '''
        self.doc_diskcache.create_or_update(identifier, filelike)

    def add_blob(self, identifier, filelike): 
        ''' add (create or fail) a blob in the storage vault
        @raise KeyError: if store to vault fails
        '''
        logger = logging.getLogger()
        logger.debug("add_blob (%s), filelike is %s" % (identifier, filelike))
        try:
            self.vault.add(identifier, filelike)
        except VaultError as e:
            raise KeyError("adding to storage vault resulted in an exception: {1}".format(e))

    def prime_blob(self, identifier=None, mimetype='application/pdf', wait=True):
        ''' load blob from storage vault, cache blob, optional rerender pages (if application/pdf), cache pages.
        @return: returns success, identifier, response if wait==True else: True, identifier, ""
        '''
        result = do_rendering.delay(identifier, mimetype)
        
        if wait: # we wait for an answer, meaning rendering is async, but view waits
            success, used_identifier, response = result.get()
            if not success:
                logger = logging.getLogger()
                if str(identifier) != str(used_identifier):
                    logger.error("prime_blob could not get_blob(%s), exception was %r" % (identifier, response))
                else:
                    logger.error("prime_blob of blob %s returned an IOError: %r" % (identifier, response))
                    
            return success, used_identifier, response
        else:
            return True, identifier, ""
      
    def get_blob(self, identifier, try_diskcache=True, try_vault=True):
        '''get a blob (unidentified media data) either from caches, or from storage vault
        @raise KeyError: if reading the data of the identifier went wrong 
        '''
        filelike=None
                
        if try_diskcache:
            filelike = self.doc_diskcache.get(identifier, touch_accesstime=True)
        
        if not filelike and try_vault and identifier:
            try:
                filelike = self.vault.get(identifier)
                self.doc_diskcache.create_or_update(identifier, filelike)
            except Exception as exceptobj:
                raise KeyError, "could not load blob with identifier %s, exception was %r" % (identifier, exceptobj)
            finally:
                self.vault.decommission(filelike)    
            
            filelike = self.doc_diskcache.get(identifier)
        
        if not filelike:
            raise KeyError, "could not load blob with identifier %s" % (identifier)

        return filelike

    def get_branded(self, identifier, mimetype='application/pdf', branding=None):
        ''' get a branded blob (identified by mimetype) either from caches, or from storage vault and re-render branding
        @raise KeyError: if reading the data of the identifier went wrong 
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

    def set_page(self, page, filelike, use_render_memcache=False, use_render_diskcache=False):
        ''' set (create or update) a picture of an page of an document
        @param page: ecs.utils.pdfutils.Page Object
        '''
        identifier = str(page)
        if use_render_memcache:
            self.render_memcache.create_or_update(identifier, filelike)
        if use_render_diskcache:
            self.render_diskcache.create_or_update(identifier, filelike)

    def get_page(self, page, try_memcache=True, try_diskcache=True):
        ''' get a picture of an page of an document  
        @param page: ecs.utils.pdfutils.Page Object 
        @raise KeyError: if page could not be loaded 
        '''
        filelike = None
        identifier = str(page)
        
        if try_memcache:     
            filelike = self.render_memcache.get(identifier)
        
        if filelike:
            self.render_diskcache.touch_accesstime(identifier) # update access in page diskcache
        else:
            if try_diskcache:
                filelike = self.render_diskcache.get(identifier, touch_accesstime=True) 
                if filelike:
                    self.doc_diskcache.touch_accesstime(page.id) # but update access in document diskcache
                else: 
                    # still not here, so we need to recache from scratch
                    success, used_identifier, additional_msg = self.prime_blob(page.id, mimetype='application/pdf', wait=True)
                    if not success: 
                        raise KeyError, "could not load page for document %s, error was %s" % (identifier, additional_msg)
                    else:
                        filelike = self.render_diskcache.get(identifier)
                        
                self.render_memcache.create_or_update(identifier, filelike)
                filelike.seek(0)
        return filelike


class VolatileCache:
    '''
    volatile, key/value, self aging, fixed size cache using memcached
    @warning: Storing values larger than 1MB requires recompiling/reconfiguring memcached and may not be supported
    '''

    def __init__(self):
        if settings.MS_SERVER ["render_memcache_lib"] == 'memcache':
            import memcache as memcache
        elif settings.MS_SERVER ["render_memcache_lib"] == 'mockcache' or settings.MS_SERVER ["render_memcache_lib"] == '' :
            import mockcache as memcache
        else:
            raise NotImplementedError('i do not know about %s as render_memcache_lib' % settings.MS_SERVER ["render_memcache_lib"])

        self.ns = '%s.ms' % getpass.getuser()
        self.mc = memcache.Client(['%s:%d' % (settings.MS_SERVER ["render_memcache_host"],
            settings.MS_SERVER ["render_memcache_port"])], debug=False)

    def create_or_update(self, identifier, filelike):
        ''' create_or_update (set) data value of identifier) '''
        if hasattr(filelike,"read"):
            self.mc.set("".join((identifier, self.ns)), filelike.read())
        else:
            self.mc.set("".join((identifier, self.ns)), filelike)
        
    def get(self, identifier):
        ''' get data value of identifier 
        @return: The value or None.
        '''
        return self.mc.get("".join((identifier, self.ns)))

    def entries(self):
        ''' dump all values ''' 
        return self.mc.dictionary.values() 


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
            return (int(expires) > int(time.time()) and expected_signature == signature)
    
    def verify(self, urlstring):
        bucket, objectid, keyId, expires, signature = self.parse(urlstring)
        return self.verify_parsed(bucket, objectid, keyId, expires, signature)
