'''
Created on Aug 19, 2010

@author: amir
'''

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
        self._prepare_root_dir()

    def add(self, identifier, filelike):
        print "identifier: ", identifier
        if not self.exists(identifier):
            
            path = self._generate_path(identifier)
            print "path:", path
            os.makedirs(os.path.dirname(path), DiskBuckets.DEFAULT_MKDIR_MODE)
            if hasattr(filelike, "read"):
                open(path, "wb").write(filelike.read())
            else:
                open(path, "wb").write(filelike)
        else:
            raise KeyError('Entry already exists: ' + identifier)  

    def get(self, identifier):
        if self.exists(identifier):
            return open(self._generate_path(identifier), "rb")
        else: 
            raise KeyError('Entry not found: ' + identifier)

    def exists(self, identifier):
        path = self._generate_path(identifier) 
        return os.path.isfile(path) and not os.path.islink(path);
            
    def _prepare_root_dir(self):
        if self.allow_mkrootdir and not os.path.isdir(self.root_dir):
            os.makedirs(self.root_dir, DiskBuckets.DEFAULT_MKDIR_MODE)

    def _generate_path(self, identifier):
        path=''
        for token in identifier[:self.maxdepth-1]: 
            path = os.path.join(path, token)
        result =  os.path.join(self.root_dir, path, identifier)
        print "res: ",result
        return result

