'''
Created on Aug 26, 2010

@author: amir
'''
import getpass
import os
import pickle

from django.conf import settings
from ecs.mediaserver.diskbuckets import DiskBuckets
from ecs.mediaserver.docshot import Docshot
from ecs.mediaserver.renderer import Renderer
from StringIO import StringIO

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

    def store(self, cacheable, use_render_memcache=False, use_render_diskcache=False, use_doc_diskcache=False, use_vault=False):
        if use_render_memcache:
            self.render_memcache.store(cacheable);
        if use_render_diskcache:
            self.render_diskcache.store(cacheable);
        if use_doc_diskcache:
            self.doc_diskcache.store(cacheable);
        if use_vault:
            cid = cacheable.cacheID()
            self.vault.add(cid, cacheable.getData());

    def fetch(self, cacheable, try_render_memcache=False, try_render_diskcache=False, try_doc_diskcache=False, try_vault=True):
        print "fetch"
        filelike=None
        
        if try_render_memcache:        
            filelike = self.render_memcache.fetch(cacheable);
    
        if not filelike and try_render_diskcache:
            filelike = self.render_diskcache.fetch(cacheable);

        if not filelike and try_doc_diskcache:
            filelike = self.doc_diskcache.fetch(cacheable);
                        
        if not filelike and try_vault:
            filelike = self.vault.get(cacheable.cacheID())
            cacheable.setData(filelike.read())
            self._cachePdfDocument(cacheable)
            self._cacheDocshots(cacheable)
 
        return filelike
 
    def _cachePdfDocument(self, document):
        if document:
            self.doc_diskcache.store(document)

    def _cacheDocshots(self, document):
        for docshot in self._createDefaultDocshots(document):
            self.render_diskcache.store(docshot)

    def _createDefaultDocshots(self, document):
        tiles = [ 1, 3, 5 ]
        width = [ 800, 768 ] 
        docshots = []
 
        for t in tiles:
            for w in width:
                docshots.extend(self.renderer.renderPDFMontage(document, w, t, t)) 
        
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

        def store(self, cacheable):
            self.mc.set(cacheable.cacheID(), cacheable)
            
        def fetch(self, cacheable):
            cacheable = self.mc.get(cacheable.cacheID())
            if cacheable: 
                cacheable.touch()

            return StringIO(cacheable.getData())
            
        def age(self):
            entriesByAge = self.entries_by_age()
            cachesize = self.size()
            
            while cachesize < self.maxsize:
                oldest = entriesByAge.next();
                size = os.path.getsize(oldest)
                os.remove(oldest)
                cachesize -= size
            
        def entries_by_age(self):
            return list(reversed(sorted(self.entries(), key=Cacheable.lastaccess)))

        def entries(self):
            return self.mc.dictionary.values() 
        
        def size(self):
            sum(len(entry.data) for entry in self.entries())

class DiskCache(object):
        def __init__(self):
            self.cachedir = "/tmp"
            self.maxsize = 1024 * 1024 * 10

        def store(self, cacheable):
            path=os.path.join(self.cachedir, cacheable.cacheID());
            print "diskcache store", cacheable, " ",cacheable.cacheID(), " ", path
            if not os.path.exists(path):
                f = open(path, 'wb')
                f.write(cacheable.getData())
                f.close()
                return True
            else:
                return False
             
        def fetch(self, cacheable):
            path=self._internal_path(cacheable)

            print "diskcache path", path
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
            return os.listdir(os.path.join(self.cachedir, "*"))
