# -*- coding: utf-8 -*-

import os, getpass, tempfile

from django.conf import settings

from ecs.utils.pathutils import tempfilecopy
from ecs.utils.storagevault import getVault
from ecs.utils.diskbuckets import DiskBuckets
from ecs.utils.pdfutils import pdf_isvalid
from ecs.utils import gpgutils

from ecs.mediaserver.renderer import renderDefaultDocshots
 
 
class DocumentProvider(object):
    '''
    The central document storage and retrieval facility.
    Implements caching layers and rules as well as storage logic
    '''

    def __init__(self):
        self.render_memcache = VolatileCache()
        self.render_diskcache = DiskCache(os.path.join(settings.MS_SERVER ["render_diskcache"], "docshots"),
            settings.MS_SERVER ["render_diskcache_maxsize"])
        self.doc_diskcache = DiskCache(os.path.join(settings.MS_SERVER ["doc_diskcache"], "blobs"),
            settings.MS_SERVER ["doc_diskcache_maxsize"])
        self.vault = getVault()


    def addBlob(self, mediablob, filelike): # xxx: this is a test function and should not be used normal
        self.vault.add(mediablob.cacheID(), filelike);

        
    def addDocshot(self, docshot, filelike, use_render_memcache=False, use_render_diskcache=False):
        if use_render_memcache:
            self.render_memcache.create_or_update(docshot.cacheID(), filelike)
        if use_render_diskcache:
            self.render_diskcache.create_or_update(docshot.cacheID(), filelike)
       
    
    def getBlob(self, mediablob, try_doc_diskcache=True, try_vault=True, rerender_always=False):
        filelike=None
        
        if try_doc_diskcache:
            filelike = self.doc_diskcache.get(mediablob.cacheID());
        
        if not filelike and try_vault:
            filelike = self._getBlob(mediablob)
            rerender_always = True
            
        if rerender_always == True and filelike is not None:
            if not self._cacheDocshots(mediablob, filelike):
                print "caching of docshots went wrong"
 
        return filelike


    def getDocshot(self, docshot, try_render_memcache=True, try_render_diskcache=True):
        filelike = None
        
        if try_render_memcache:     
            filelike = self.render_memcache.get(docshot.cacheID());
        
        if filelike:
            self.render_diskcache.update_access(docshot.cacheID()) # update access in docshot cache
            self.doc_diskcache.update_access(docshot.mediablob.cacheID()) # update access in mediablob cache
        else:
            if try_render_diskcache:
                filelike = self.render_diskcache.get(docshot.cacheID()) # do not update access because get of diskcache makes it
                if not filelike: # still not here, so we need to recache from scratch
                    filelike = self.getBlob(docshot.mediablob, rerender_always=True) # This primes caches
                    if not filelike:
                        return None
                self.render_memcache.add(docshot.cacheID(), filelike)
                filelike.seek(0)
        return filelike

 
    def _getBlob(self, mediablob):        
        filelike = self.vault.get(mediablob.cacheID())
        if not filelike:
            return None 
        elif hasattr(filelike, "name"):
            inputfilename = filelike.name
        else:
            inputfilename = tempfilecopy(filelike) 
        
        try:
            osdescriptor, decryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)
            gpgutils.decrypt(inputfilename, decryptedfilename, settings.STORAGE_DECRYPT["gpghome"],
                settings.STORAGE_DECRYPT ["owner"])
        except IOError as exceptobj:
            raise # FIXME: if something fails here (decryption of blob) it should return some error

        with open(decryptedfilename, "rb") as filelike:
            self._cacheBlob(mediablob, filelike)
        
        filelike = self.doc_diskcache.get(mediablob.cacheID());
        return filelike


    def _cacheBlob(self, mediablob, filelike):
        self.doc_diskcache.create_or_update(mediablob.cacheID(), filelike)


    def _cacheDocshots(self, pdfblob, filelike):
        from ecs.mediaserver.task_queue import rerender_docshots
        
        if not pdf_isvalid(filelike):
            return False
        
        result = rerender_docshots(pdfblob)
        return result


        
class VolatileCache(object):
    '''
    A volatile cache using memcache
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
    '''
    Persistent cache using directory buckets which are derived from the cache id of storage unit
    '''
    def __init__(self, root_dir, maxsize):
        self.maxsize = maxsize
        super(DiskCache, self).__init__(root_dir, allow_mkrootdir=True)

    def add(self, identifier, filelike):
        super(DiskCache, self).add(identifier, filelike)
    
    def create_or_update(self, identifier, filelike):
        super(DiskCache, self).create_or_update(identifier, filelike)
             
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

