'''
Created on Aug 26, 2010

@author: amir
'''
import getpass
import os

from django.conf import settings
from ecs.mediaserver.diskbuckets import DiskBuckets
from ecs.mediaserver.renderer import Renderer


class DocumentProvider(object):
    '''
    classdocs

    '''
    renderer = Renderer() 
    
    def __init__(self):
        
        self.render_memcache = VolatileCache()
        self.render_diskcache = DiskCache()
        self.doc_diskcache = DiskCache()
        self.vault = DiskBuckets("/tmp/diskbucket", allow_mkrootdir=True)

    def addDocshot(self, docshotModel, filelike, use_render_memcache=False, use_render_diskcache=False):
        if use_render_memcache:
            self.render_memcache.add(docshotModel.cacheID(), filelike)
        if use_render_diskcache:
            self.render_diskcache.add(docshotModel.cacheID(), filelike)
           

    def addPdfDocument(self, pdfDocModel, filelike):
        self.vault.add(pdfDocModel.cacheID(), filelike);
    
    def getPdfDocument(self, pdfDocModel, try_doc_diskcache=True, try_vault=True):
        filelike=None
            
        if try_doc_diskcache:
            filelike = self.doc_diskcache.get(pdfDocModel);
                        
        if not filelike and try_vault:
            filelike = self.vault.get(pdfDocModel.cacheID())
            self._cachePdfDocument(pdfDocModel, filelike)
            self._cacheDocshots(pdfDocModel, filelike)
 
        return filelike

    def getDocshot(self, docshotModel, try_render_memcache=True, try_render_diskcache=True):
        filelike=None
        
        if try_render_memcache:     
            filelike = self.render_memcache.get(docshotModel);
    
        if not filelike and try_render_diskcache:
            filelike = self.render_diskcache.get(docshotModel.cacheID());
            self.render_memcache.store(docshotModel.cacheID(), filelike)
            filelike.seek(0)
   
        return filelike
 
    def __cachePdfDocument(self, pdfDocModel, filelike):
        self.doc_diskcache.store(pdfDocModel.cacheID(), filelike)

    def __cacheDocshots(self, pdfDocModel, filelike):
        for docshot in self._createDefaultDocshots(pdfDocModel,filelike):
            self.render_diskcache.store(docshot)

    def __createDefaultDocshots(self, pdfDocModel, filelike):
        tiles = [ 1, 3, 5 ]
        width = [ 800, 768 ] 
        docshots = []
 
        for t in tiles:
            for w in width:
                docshots.extend(self.renderer.renderPDFMontage(pdfDocModel, filelike, w, t, t)) 
        
        return docshots
    

class VolatileCache(object):
        def __init__(self):
            if settings.RENDERSTORAGE_LIB == 'memcache':
                import memcache as memcache
            elif settings.RENDERSTORAGE_LIB == 'mockcache' or settings.RENDERSTORAGE_LIB == '' :
                import mockcache as memcache
                print "Debug: Import mockcache as memcache"
            else:
                raise NotImplementedError('i do not know about %s as RENDERSTORAGE_LIB' % settings.RENDERSTORAGE_LIB)
    
            self.ns = '%s.ms' % getpass.getuser()
            self.mc = memcache.Client(['%s:%d' % (settings.RENDERSTORAGE_HOST, settings.RENDERSTORAGE_PORT)], debug=False)
            self.maxsize = 1024 * 1024 * 10

        def add(self, uuid, filelike):
            self.mc.set(uuid, filelike)
            
        def get(self, uuid):
                return self.mc.get(uuid)
            
        def entries(self):
            return self.mc.dictionary.values() 
        
class DiskCache(DiskBuckets):
        def __init__(self):
            self.cachedir = "/tmp"
            self.maxsize = 1024 * 1024 * 10
            super(DiskCache, self).__init__(self.cachedir)

        def add(self, uuid, filelike):
            super(DiskCache, self).add(uuid, filelike)
             
        def get(self, uuid):
            path=self._internal_path(uuid)

            if os.path.exists(path):
                os.utime(path, None)
                return open(path, "r")
                
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

        def _internal_path(self, cacheable):
            return os.path.join(self.cachedir, cacheable.cacheID())
            
        def _raw_entries(self):
            files = os.walk(self.cachedir)
            return files
