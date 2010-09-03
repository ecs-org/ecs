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

    def store(self, cacheable, use_render_memcache=False, use_render_diskcache=False, use_doc_diskcache=False, vault=False):
        if use_render_memcache:
            self.render_memcache.store(cacheable);
        if use_render_diskcache:
            self.render_diskcache.store(cacheable);
        if use_doc_diskcache:
            self.doc_diskcache.store(cacheable);
        if vault:
            cid = cacheable.cacheID()
            print "vault cache id:", cid
            self.vault.add(cid, cacheable.getData());

    def fetch(self, cacheable, try_render_memcache=False, try_render_diskcache=False, try_doc_diskcache=False, try_vault=False):
        stored=None
        
        if try_render_memcache:        
            stored = self.render_memcache.fetch(cacheable);
    
        if not stored and try_render_diskcache:
            stored = self.render_diskcache.fetch(cacheable);

        if not stored and try_doc_diskcache:
            stored = self.doc_diskcache.fetch(cacheable);
                        
        if not stored and try_vault:
            stored = self.try_vault.get(cacheable.cacheID());
            self._cachePdfDocument(stored)
            

        return stored
 
    def _cachePdfDocument(self, document):
        if document:
            self.doc_diskcache.store(document)


    def _render_and_cacheDocshots(self, document):
        if document:
            self.doc_diskcache.store(document)
            
        for docshot in self._createDefaultDocshots(document):
            pass

    def _createDefaultDocshots(self, document):
        return [ Docshot(1, 1, 800, 0, document.numpages, document.uuid),
        Docshot(1, 1, 768, 0, document.numpages, document.uuid),
        Docshot(3, 3, 800, 0, document.numpages, document.uuid),
        Docshot(5, 5, 800, 0, document.numpages, document.uuid),
        Docshot(3, 3, 768, 0, document.numpages, document.uuid),
        Docshot(5, 5, 768, 0, document.numpages, document.uuid) ]

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

            return cacheable
            
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
            
            if not os.path.exists(path):
                pickle.dump(cacheable, open(path, 'wb'))
                return True
            else:
                return False
             
        def fetch(self, cacheable):
            path=self._internal_path(cacheable)
            
            if os.path.exists(path):
                cacheable = pickle.load(open(path, "r"))
                if cacheable:
                    cacheable.touch()   
                    return cacheable
                
            return None
            
        def age(self):
            entriesByAge = self.entries_by_age()
            cachesize = self.size()
            
            while cachesize < self.maxsize:
                oldest = entriesByAge.next();
                path = self._internal_path(oldest)
                size = os.path.getsize(path)
                os.remove(path)
                cachesize -= size

        def entries_by_age(self):
            return list(reversed(sorted(self.entries(), key=Cacheable.lastaccess)))

        def entries(self):
            return [pickle.load(path) for path in self._raw_entries()]

        def size(self):
            return sum(os.path.getsize(entry) for entry in self._raw_entries())

        def _internal_path(self, cacheable):
            return os.path.join(self.cachedir, cacheable.cacheID())
            
        def _raw_entries(self):
            return os.listdir(os.path.join(self.cachedir, "*"))
