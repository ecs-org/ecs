# -*- coding: utf-8 -*-

import os, getpass, tempfile

from django.conf import settings

from ecs.utils.pathutils import tempfilecopy
from ecs.utils.storagevault import getVault
from ecs.utils.diskbuckets import DiskBuckets  
from ecs.utils.gpgutils import decrypt_verify
from ecs.mediaserver.tasks import rerender_pages
 
 
class MediaProvider(object):
    '''
    a central document storage and retrieval facility.
    Implements caching layers, rules, storage logic
    '''

    def __init__(self):
        self.render_memcache = VolatileCache()
        self.render_diskcache = DiskCache(os.path.join(settings.MS_SERVER ["render_diskcache"], "pages"),
            settings.MS_SERVER ["render_diskcache_maxsize"])
        self.doc_diskcache = DiskCache(os.path.join(settings.MS_SERVER ["doc_diskcache"], "blobs"),
            settings.MS_SERVER ["doc_diskcache_maxsize"])
        self.vault = getVault()


    def _addBlob(self, identifier, filelike): 
        ''' xxx: this is a test function and should not be used normal '''
        self.vault.add(identifier, filelike)

        
    def getBlob(self, identifier, try_diskcache=True, try_vault=True):
        filelike=None
        
        if try_diskcache:
            filelike = self.doc_diskcache.get(identifier)
        
        if not filelike and try_vault and identifier:
            filelike = self.vault.get(identifier)
            if hasattr(filelike, "name"):
                inputfilename = filelike.name
            else:
                inputfilename = tempfilecopy(filelike) 
            
            try:
                osdescriptor, decryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)
                decrypt_verify(inputfilename, decryptedfilename, settings.STORAGE_DECRYPT["gpghome"],
                    settings.STORAGE_DECRYPT ["owner"])
            except IOError as exceptobj:
                raise # FIXME: if something fails here (decryption of blob) it should return some error
    
            with open(decryptedfilename, "rb") as decryptedfilelike:
                self.doc_diskcache.create_or_update(identifier, decryptedfilelike)

            filelike = self.doc_diskcache.get(identifier)
        return filelike


    def setPage(self, page, filelike, use_render_memcache=False, use_render_diskcache=False):
        ''' set (create or update) a picture of an page of an document
        @param page: ecs.utils.pdfutils.Page Object
        '''
        identifier = str(page)
        if use_render_memcache:
            self.render_memcache.set(identifier, filelike)
        if use_render_diskcache:
            self.render_diskcache.create_or_update(identifier, filelike)


    def getPage(self, page, try_memcache=True, try_diskcache=True):
        ''' get a picture of an page of an document  
        @param page: ecs.utils.pdfutils.Page Object 
        '''
        filelike = None
        identifier = str(page)
        
        if try_memcache:     
            filelike = self.render_memcache.get(identifier)
        
        if filelike:
            self.render_diskcache.touch_accesstime(identifier) # update access in page cache
        else:
            if try_diskcache:
                filelike = self.render_diskcache.get(identifier) 
                if filelike:
                    self.doc_diskcache.touch_accesstime(page.id) # but update access in document diskcache
                else: 
                    if not rerender_pages(page.id): # still not here, so we need to recache from scratch
                        return None
                    else:
                        filelike = self.render_diskcache.get(identifier)
                        if not filelike:
                            return None

                self.render_memcache.set(identifier, filelike)
                filelike.seek(0)
        return filelike

 

class VolatileCache(object):
    '''
    A volatile, key/value, self aging, fixedsize cache using memcache
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

    def set(self, identifier, filelike):
        ''' set (create_or_update) data value of identifier) '''
        # FIXME: self.ns (identifier part which is the current running os user of the process) should be incooperated into memcache identifier to avoidentifier collissions
        if hasattr(filelike,"read"):
            self.mc.set(identifier, filelike.read())
        else:
            self.mc.set(identifier, filelike)
        
    def get(self, identifier):
        ''' get data value of identifier '''
        return self.mc.get(identifier)

    def entries(self):
        ''' dump all values ''' 
        return self.mc.dictionary.values() 



class DiskCache(DiskBuckets):
    '''
    Persistent cache using directory buckets which are derived from the cache identifier of storage unit
    '''
    def __init__(self, root_dir, maxsize):
        self.maxsize = maxsize
        super(DiskCache, self).__init__(root_dir, allow_mkrootdir=True)

    def add(self, identifier, filelike):
        super(DiskCache, self).add(identifier, filelike)
    
    def create_or_update(self, identifier, filelike):
        super(DiskCache, self).create_or_update(identifier, filelike)
             
    def touch_accesstime(self, identifier):
        os.utime(self._generate_path(identifier), None)

    def get(self, identifier):
        if self.exists(identifier):
            self.touch_accesstime(identifier)
            return super(DiskCache, self).get(identifier)
        else:
            return None
        
    def age(self):
        entriesByAge = self.entries_by_age()
        cachesize = self.size()
        
        while cachesize < self.maxsize:
            oldest = entriesByAge.next()
            size = os.path.getsize(oldest)
            os.remove(oldest)
            cachesize -= size

    def entries_by_age(self):
        return list(reversed(sorted(self.entries(), key=os.path.getatime)))

    def entries(self):
        return [open(path,"rb") for path in os.walk(self.root_dir)]

    def size(self):
        return sum(os.path.getsize(entry) for entry in os.walk(self.root_dir))


