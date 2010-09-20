'''
Created on Aug 26, 2010

@author: amir
'''
import getpass
import os

from django.conf import settings
from ecs.utils.storagevault import getVault
from ecs.utils.diskbuckets import DiskBuckets
from ecs.mediaserver.renderer import renderDefaultDocshots
from ecs.utils.pdfutils import pdf_isvalid
import tempfile
 
class DocumentProvider(object):
    '''
    
    '''
    def __init__(self):
        self.render_memcache = VolatileCache()
        self.render_diskcache = DiskCache(os.path.join(settings.RENDER_DISKCACHE, "docshots"), settings.RENDER_DISKCACHE_MAXSIZE)
        self.doc_diskcache = DiskCache(os.path.join(settings.DOC_DISKCACHE, "blobs") , settings.DOC_DISKCACHE_MAXSIZE)
        self.vault = getVault()
        
    def addDocshot(self, docshot, filelike, use_render_memcache=False, use_render_diskcache=False):
        if use_render_memcache:
            self.render_memcache.add(docshot.cacheID(), filelike)
        if use_render_diskcache:
            self.render_diskcache.add(docshot.cacheID(), filelike)
           
    def addBlob(self, mediablob, filelike):
        self.vault.add(mediablob.cacheID(), filelike);
    
    def getBlob(self, mediablob, try_doc_diskcache=True, try_vault=True):
        filelike=None
            
        if try_doc_diskcache:
            filelike = self.doc_diskcache.get(mediablob.cacheID());
                        
        if not filelike and try_vault:
            filelike = self.vault.get(mediablob.cacheID())
            self._cacheBlob(mediablob, filelike)
            self._cacheDocshots(mediablob, filelike)
 
        return filelike

    def getDocshot(self, docshot, try_render_memcache=True, try_render_diskcache=True):
        filelike=None
        
        if try_render_memcache:     
            filelike = self.render_memcache.get(docshot);
        
        if filelike:
            self.render_diskcache.update_access(docshot.cacheID()) # update access in docshot cache
            self.doc_diskcache.update_access(docshot.mediablob.cacheID())   # update access in mediablob cache
        else:
            if try_render_diskcache:
                filelike = self.render_diskcache.get(docshot.cacheID()) # do not update access because get of diskcache makes it

                if not filelike: # still not here, so we need to recache from scratch
                    self.getBlob(docshot.mediablob) # This primes caches
                    
                    filelike = self.render_diskcache.get(docshot.cacheID())
                    if not filelike:
                        return None
                        
                self.render_memcache.add(docshot.cacheID(), filelike)
                filelike.seek(0)
        return filelike
 
    def _cacheBlob(self, mediablob, filelike):
        self.doc_diskcache.add(mediablob.cacheID(), filelike)

    def _cacheDocshots(self, pdfblob, filelike):
        if not pdf_isvalid(filelike):
            return False
        
        for docshot, data in renderDefaultDocshots(pdfblob,filelike):
            self.addDocshot(docshot, data, use_render_diskcache=True)
        return True
               
class VolatileCache(object):
    def __init__(self):
        # TODO configure memcache qoutas
        if settings.RENDER_MEMCACHE_LIB == 'memcache':
            import memcache as memcache
        elif settings.RENDER_MEMCACHE_LIB == 'mockcache' or settings.RENDER_MEMCACHE_LIB == '' :
            import mockcache as memcache
            print "Debug: Import mockcache as memcache"
        else:
            raise NotImplementedError('i do not know about %s as RENDER_MEMORYSTORAGE_LIB' % settings.RENDER_MEMCACHE_LIB)

        self.ns = '%s.ms' % getpass.getuser()
        self.mc = memcache.Client(['%s:%d' % (settings.RENDER_MEMCACHE_HOST, settings.RENDER_MEMCACHE_PORT)], debug=False)

    def add(self, identifier, filelike):
        # FIXME: self.ns (identifier part which is the current running os user of the process) should be incooperated into memcache identifier to avoid collissions
        if hasattr(filelike,"read"):
            self.mc.set(identifier, filelike.read())
        else:
            self.mc.set(identifier, filelike)
        
    def get(self, uuid):
        return self.mc.get(uuid)

    def entries(self):
        return self.mc.dictionary.values() 
        
class DiskCache(DiskBuckets):
        def __init__(self, root_dir, maxsize):
            self.maxsize = maxsize
            super(DiskCache, self).__init__(root_dir, allow_mkrootdir=True)

        def add(self, identifier, filelike):
            super(DiskCache, self).add(identifier, filelike)
             
        def update_access(self, identifier):
            os.utime(self._generate_path(identifier), None)

        def get(self, uuid):
            if self.exists(uuid):
                self.update_access(uuid)
                return super(DiskCache, self).get(uuid)
            else:
                return None
            
        def age(self):
            entriesByAge = self.entries_by_age()
            cachesize = self.size()
            
            while cachesize < self.maxsize:
                oldest = entriesByAge.next();
                size = os.path.getsize(oldest)
                os.remove(oldest)
                cachesize -= size

        def entries_by_age(self):
            return list(reversed(sorted(self.entries(), key=os.path.getatime)))

        def entries(self):
            return [open(path,"rb") for path in self._raw_entries()]

        def size(self):
            return sum(os.path.getsize(entry) for entry in self._raw_entries())

        def _raw_entries(self):
            files = os.walk(self.root_dir)
            return files
