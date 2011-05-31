# -*- coding: utf-8 -*-
'''
===========
Diskbuckets
===========

A read/write/overwrite/purge/age key-value store featuring
 * simple, using the filesystem builtin features to organize large number of items support -- values can be 0 > big > 500mb 
 * transparent encryption+signing for storing data and decryption+verify support for retrieving data
 * easy to extent base class (StorageVault) for writing other StorageVault backend connectors 
    
Usage
=====

.. code-block:: python
   
   pass

'''

import os, time
from operator import itemgetter


class BucketError(Exception):
    ''' Base class for exceptions for diskbuckets; Derived from Exception'''
    pass

class BucketKeyError(BucketError, KeyError):
    ''' Exception class raised on KeyError (key not found) exceptions '''
    pass

class BucketIOError(BucketError, EnvironmentError):
    ''' Exception class raised on IO / Environment exceptions '''
    pass
    

class DiskBuckets(object):
    ''' stores binary data associated to a identifier into a filesystem directory tree optimized for many files.
    the directory tree is derived from the identifier. 
    update access time support on get (optional).
    aging (delete items) support with variable criteria how to age entries and when to stop.
    @raise BucketError, BucketKeyError, BucketIOError 
    '''
    DEFAULT_MKDIR_MODE=0777
    
    def __init__(self, root_dir, max_size=0, allow_mkrootdir=False, max_depth=5):
        '''
        @param root_dir: root dir of the bucket tree
        @param max_depth: max_depth of the bucket tree
        @param allow_mkrootdir: allow creation of the root directory if it doesn't exist
        '''
        self.root_dir = os.path.abspath(root_dir)
        self.max_depth = max_depth
        self.max_size = max_size
        self.allow_mkrootdir = allow_mkrootdir
        if self.allow_mkrootdir and not os.path.isdir(self.root_dir):
            try:
                os.makedirs(self.root_dir, DiskBuckets.DEFAULT_MKDIR_MODE)
            except EnvironmentError as e:
                raise BucketIOError(e)

    def _generate_path(self, identifier):
        path=''
        if len(identifier) < (self.max_depth-1):
            raise KeyError("Error: len of identifier is not compatible with diskbuckets, is: {0}, should >= {1}".format(len(identifier), self.max_depth))
            
        for token in identifier[:self.max_depth-1]:
            path = os.path.join(path, token)
        result =  os.path.join(self.root_dir, path, identifier)
        return result

    def _bucket_iter(self):
        ''' Generator of filename, size, last-modified (ctime) tuple of bucket entries (not sorted)
        @note: swallows EnvironmentError's while retrieving size or accesstime of file (0 and time.time() of iter lifetime begin is substituted)
        @raise BucketIOError: if os.walk returns EnvironmentError
        '''
        current_ctime = time.time()
        try:                
            for root, dirs, files in os.walk(self.root_dir):
                for name in files:
                    f, s, m = os.path.join(root, name), 0, current_ctime
    
                    try:
                        s = os.path.getsize(f)
                    except EnvironmentError:
                        pass
                    try:
                        m = os.path.getmtime(f)
                    except EnvironmentError:
                        pass
                     
                    yield [f,s,m]
        except EnvironmentError as e:
            raise BucketIOError(e)
        
    def touch_accesstime(self, identifier):
        ''' set last access time of identifier to now
        @raise BucketIOError: update of access time fails '''
        try:
            os.utime(self._generate_path(identifier), None)
        except EnvironmentError as e:
            raise BucketIOError(e)
    
    def add(self, identifier, filelike):
        ''' add (create) new content using identifier as key
        @param filelike.read() is used if exists, else filelike itself for content
        @raise BucketKeyError: if entry of identifier already exists
        @raise BucketIOError: if can not create directory of target file or target file
        '''
        if self.exists(identifier):
            raise BucketKeyError('Entry %s already exists at storage: %s' % (identifier, self._generate_path(identifier)))
        else:
            path = self._generate_path(identifier)
            bucketdir = os.path.dirname(path)
            try:
                if not os.path.isdir(bucketdir):
                    os.makedirs(bucketdir, DiskBuckets.DEFAULT_MKDIR_MODE)
    
                if hasattr(filelike, "read"):
                    open(path, "wb").write(filelike.read())
                else:
                    open(path, "wb").write(filelike)
            except EnvironmentError, e:
                raise BucketIOError(e)

    def create_or_update(self, identifier, filelike):
        ''' delete if exists and recreate new content using identifier as key
        @raise BucketIOError: if key identifier exists, but could not be located and/or purged before (re)adding
        @raise BucketIOError: if content of key identifier could not be stored
        @raise BucketKeyError: if create_or_update was not able to update key identifier
        '''
        if self.exists(identifier):
            self.purge(identifier)
        self.add(identifier, filelike)
    
    def get(self, identifier, touch_accesstime=False):
        ''' retrieve content of key identifier and return as file object
        @param touch_accesstime: if True, file mtime will get touched to now; Warning: this will fail silently.
        @return open file object for reading
        @raise BucketKeyError: if entry with identifier not found
        @raise BucketIOError: if reading entry fails
        '''
        if not self.exists(identifier):
            raise BucketKeyError('Entry not found: ' + identifier)

        try:
            f= open(self._generate_path(identifier), "rb")
        except EnvironmentError, e:
            raise BucketIOError(e)
    
        if touch_accesstime:
            try:
                self.touch_accesstime(identifier)
            except BucketIOError:
                pass
    
        return f 

    def get_or_None(self, identifier, touch_accesstime=False):
        ''' retrieve content of key identifier and return as file object
        @param touch_accesstime: if True, file mtime will get touched to now; Warning: this will fail silently.
        @return open file object for reading, or None on any error
        '''
        try:
            r = self.get(identifier, touch_accesstime)
        except BucketError as e:
            return None
        return r
    
    def purge(self, identifier):
        ''' deletes data associated with identifier from disk
        @raise BucketKeyError: if identifier does not exist
        @raise BucketIOError: if removing of file was not successful
        '''
        if self.exists(identifier):
            try:
                os.remove(self._generate_path(identifier))
            except EnvironmentError, e:
                raise BucketIOError(e)
        else:
            raise BucketKeyError("identifier does not exist {1}".format(identifier))

    def exists(self, identifier): 
        ''' returns true if content of identifier exists
        @raise BucketIOError: if os.path.exists of path throws environment error
        '''
        e = False
        
        try:
            e = os.path.exists(self._generate_path(identifier))#
        except EnvironmentError, e:
            raise BucketIOError(e)
        
        return e

    def age(self, sortkey=None, reverse=False, abortfunc=None, ignorefunc=None, errorfunc=None):
        ''' ages (deletes) items of bucket using sortkeyfunc sorted list while not abort_criteria remove item if ignorefunc not False
        @param sortkey: is called with tuple filename, filesize, accesstime 
            defaults to itemgetter(2) (equals accesstime)
        @param abortfunc: is called with tuple bucket_size, filename, filesize, accesstime
            aborts aging if abortfunc returns True; defaults to: bucket_size < self.max_size
        @param ignorefunc: is called with tuple filename, filesize, accesstime; 
            ignores entry selected for aging if False is returned; defaults to lambda f,s,m : False
        @param errorfunc: is called with filename, filesize, accesstime, exception (basetype EnvironmentError)
            if removing of one file fails  
        @raise BucketIOError: if removing of an entry failed and errorfunc == None
        @raise BucketError: if aging could not satisfy abortfunc until end of entry list
        @raise BucketError: if abortfunc == None (equals use default) and self.max_size == 0 (equals unlimited)
        '''
        if abortfunc == None and self.max_size == 0:
            raise BucketError("no aging abort_criteria and self.max_size == 0 (unlimited); can not age")
    
        if abortfunc == None:
            abortfunc = lambda current_size, filename, filesize, accesstime: current_size < self.max_size

        if ignorefunc == None:
            ignorefunc = lambda filename, filesize, accesstime: False

        if sortkey == None:
            sortkey = itemgetter(2)
        
        entries = sorted(self._bucket_iter(), key=sortkey, reverse=reverse)
        bucket_size = sum(entry[1] for entry in entries)
        aging_success = False
        filename , filesize, accesstime = "", 0, 0 # for error display if for has no iteration
        
        for filename, filesize, accesstime in entries:
            
            if abortfunc(bucket_size, filename, filesize, accesstime):
                aging_success = True
                break
            
            if not ignorefunc(filename, filesize, accesstime):
                try:
                    os.remove(filename)
                    bucket_size -= filesize
                except EnvironmentError as e:
                    if errorfunc:
                        errorfunc(filename, filesize, accesstime, e)
                    else:
                        raise BucketIOError(e)
        
        if not aging_success:
            raise BucketError("aging abort_criteria could not be satisfied")
        else:
            print ("self.maxsize = {0}, current_size = {1}, last_accesstime_aged = {2}".format(self.max_size, bucket_size, time.ctime(accesstime)))
    