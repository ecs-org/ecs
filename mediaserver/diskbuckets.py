'''
Created on Aug 19, 2010

@author: amir
'''

import os

class DiskBuckets(object):
    '''
    stores binary data associated to a uuid into a directory tree 
    which is directly derived from the uuid. 
    '''
    DEFAULT_MKDIR_MODE=0777
    
    def __init__(self, root_dir, maxdepth=5, allow_mkrootdir=False):
        '''
        @param root_dir: root dir of the bucket tree
        @param maxdepth: maxdepth of the bucket tree
        @param allow_mkrootdir: allow creation of the root directory if it doesn't exist
        '''
        self.root_dir = os.path.abspath(root_dir)
        self.maxdepth = maxdepth
        self.allow_mkrootdir = allow_mkrootdir
        self._prepare_root_dir()

    def add(self, uuid, filelike):
        print "uuid: ", uuid
        if not self.exists(uuid):
            
            path = self._generate_bucket_path(uuid)
            print "path:", path
            os.makedirs(os.path.dirname(path), DiskBuckets.DEFAULT_MKDIR_MODE)
            open(path, "wb").write(filelike.read())
        else:
            raise KeyError('Entry already exists: ' + uuid)  

    def get(self, uuid):
        if self.exists(uuid):
            return open(self._generate_bucket_path(uuid), "r")
        else: 
            raise KeyError('Entry not found: ' + uuid)

    def exists(self, uuid):
        path = self._generate_bucket_path(uuid) 
        return os.path.isfile(path) and not os.path.islink(path);

    def _prepare_root_dir(self):
        if self.allow_mkrootdir and not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir, DiskBuckets.DEFAULT_MKDIR_MODE)

    def _generate_bucket_path(self, uuid):
        path=''
        for token in uuid[:self.maxdepth-1]: 
            path = os.path.join(path, token)
        return os.path.join(self.root_dir, path, uuid)

