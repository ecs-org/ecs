# -*- coding: utf-8 -*-

import os

class DiskBuckets(object):
    '''
    stores binary data associated to a identifier into a directory tree 
    which is directly derived from the identifier. 
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
        if self.allow_mkrootdir and not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir, DiskBuckets.DEFAULT_MKDIR_MODE)

    def add(self, identifier, filelike):
        if self.exists(identifier):
            raise KeyError('Entry %s already exists at storage: %s' % (identifier, self._generate_path(identifier)))
        else:
            path = self._generate_path(identifier)
            bucketdir = os.path.dirname(path)
            if not os.path.isdir(bucketdir):
                os.makedirs(bucketdir, DiskBuckets.DEFAULT_MKDIR_MODE)

            if hasattr(filelike, "read"):
                open(path, "wb").write(filelike.read())
            else:
                open(path, "wb").write(filelike)

    def create_or_update(self, identifier, filelike):
        if self.exists(identifier):
            self.purge(identifier)
        self.add(identifier, filelike)

    def get(self, identifier):
        if self.exists(identifier):
            return open(self._generate_path(identifier), "rb")
        else: 
            raise KeyError('Entry not found: ' + identifier)

    def purge(self, identifier):
        if self.exists(identifier):
            os.remove(self._generate_path(identifier))
            
    def exists(self, identifier): 
        return os.path.exists(self._generate_path(identifier))

    def _generate_path(self, identifier):
        path=''
        for token in identifier[:self.maxdepth-1]: 
            path = os.path.join(path, token)
        result =  os.path.join(self.root_dir, path, identifier)
        return result

