# -*- coding: utf-8 -*-
'''
============
StorageVault
============

A Write Once, read many times key/value store featuring
 * big value support -- values can be 1MB > big > 500mb 
 * transparent encryption+signing for storing data, decryption+verify support for retrieving data
 * easy to extent base class (StorageVault) for writing other StorageVault backend connectors 
 * simple local machine implementation (LocalFileStorageVault) using diskbuckets

.. warning::
    TODO: because its not checked where potential all value data is read in memory, usage should be limited to something memory can support (eg. 500mb)
    
Usage
=====

.. code-block:: python
    vault = getVault() # get configured vault

    vault.add(identifier, filelike) 
    # adds the contents of filelike using identifier as key to the vault
    
    vault.exists(identifier)
    # returns true if content for this identifier exists in storage vault
    
    filelike = vault.get(identifier) 
    # get a temporary copy of content using identifier as key accessible using filelike
    
    vault.decommission(filelike)
    # safely remove access to temporary copy


'''

import os, tempfile

from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from ecs.utils import gpgutils

from ecs.mediaserver.diskbuckets import DiskBuckets


class VaultError(Exception):
    ''' Base class for exceptions for StorageVault; Derived from Exception'''
    pass

class VaultKeyError(VaultError, KeyError):
    ''' Exception class raised on KeyError (key not found, key already exists) exceptions '''
    pass

class VaultIOError(VaultError, EnvironmentError):
    ''' Exception class raised on IO / Environment exceptions '''
    pass

class VaultEncryptionError(VaultIOError):
    ''' Exception class raised on encryption+signing, decryption+verify errors '''
    pass


def getVault():
    ''' get the default vault implementation
    @raise ImproperlyConfigured: if settings.STORAGE_VAULT contains invalid storagevault implementation
    '''
    module, class_name = settings.STORAGE_VAULT.rsplit('.', 1)
    try:
        vault = getattr(import_module(module), class_name)
    except ImportError:
        raise ImproperlyConfigured("No Vault implementation for name: %s" % (settings.STORAGE_VAULT))
    return vault()


class StorageVault():
    ''' base class for a write once, read many times storage vault
    Features: on the fly Encryption+Signing, Decryption+Verifying
    '''
    def __init__(self):
        pass
    
    def _encrypt_sign(self, inputfilepath, outputfilepath):
        try:
            gpgutils.encrypt_sign(inputfilepath, outputfilepath, settings.STORAGE_ENCRYPT['gpghome'],
                settings.STORAGE_ENCRYPT['encrypt_owner'], settings.STORAGE_ENCRYPT['signing_owner'])
        except EnvironmentError as e:
            raise VaultEncryptionError(e)

    def _decrypt_verify(self, inputfilepath, outputfilepath):
        try:
            gpgutils.decrypt_verify(inputfilepath, outputfilepath, settings.STORAGE_ENCRYPT['gpghome'],
                settings.STORAGE_ENCRYPT['decrypt_owner'], settings.STORAGE_ENCRYPT['verify_owner'])
        except EnvironmentError as e:
            raise VaultEncryptionError(e)
        
    def _add_to_vault(self, identifier, filelike):
        raise NotImplementedError
    
    def _get_from_vault(self, identifier):
        raise NotImplementedError
    
    def add(self, identifier, filelike):
        ''' add a filelike binary data using identifier as key to vault
        @note: Does on the fly encryption+signing of content
        @raise KeyError, EnvironmentError, VaultError, VaultEncryptionError: if adding did not succeed. eg. key already exists, upload error, encryption error
        '''
        try:
            if not hasattr(filelike, 'fileno'):
                infile = tempfile.TemporaryFile(dir=settings.TEMPFILE_DIR)
                infile.write(filelike.read())
                infile.seek(0)
            else:
                infile = filelike
            
            tmp_oshandle, tmp_name = tempfile.mkstemp(); os.close(tmp_oshandle)
            
            self._encrypt_sign(infile.path, tmp_name)
            with open(tmp_name, "rb") as tmp:
                self._add_to_vault(identifier, tmp)
        finally:
            if os.path.isfile(tmp_name):
                os.remove(tmp_name)

    def get(self, identifier):
        ''' get a filelike content of key identifier from the vault
        @attention: implementers: this filelike object should **always** a temporary copy, and never the original (even in case of localstoragevault)
        @note: you should close the filelike object and remove it from disk (if real file) once done with it, using decommission(filelike)
        @raise EnvironmentError, KeyError, VaultError, VaultEncryptionError: if get, or decryption fails  
        '''
        filelike = None
        
        try:
            tmp_oshandle, tmp_name = tempfile.mkstemp(); os.close(tmp_oshandle)
            filelike = self._get_from_vault(identifier)
            
            if not hasattr(filelike, 'fileno'):
                infile = tempfile.TemporaryFile(dir=settings.TEMPFILE_DIR)
                infile.write(filelike.read())
                infile.seek(0)
            else:
                infile = filelike
                
            self._decrypt_verify(infile.path, tmp_name)
                
        finally:
            if hasattr(filelike, "fileno") and not filelike.closed():
                filelike.close()
    
    def decommission(self, filelike, silent=True):
        ''' decommission (close and delete if real file) a filelike copy object that was returned from get(identifer)
        @param silent: if True (default) it will not raise EnvironmentError in case file deletion fails
        @raise EnvironmentError: if os.remove fails and silent=False
        @note: storagevault **never** deletes or gives access to real storage data, instead a copy is served
        '''
        isrealfile = hasattr(filelike, "fileno") and hasattr(filelike, "name")
        
        if hasattr(filelike, "closed") and hasattr(filelike, "close"):
            if not filelike.closed:
                filelike.close()
        
        if isrealfile:
            filename = filelike.name
            filelike = None
            try:
                os.remove(filename)
            except EnvironmentError:
                if not silent:
                    raise
                    
    def exists(self, identifier):
        ''' returns true if content of identifier exists
        '''
        raise NotImplementedError
    
    
class LocalFileStorageVault(StorageVault):
    ''' StorageVault implementation using a local file storage (based on diskbuckets) 
    '''
    def __init__(self):
        rootdir = settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']
        self.db = DiskBuckets(rootdir, max_size = 0)
    
    def _add_to_vault(self, identifier, filelike):
        self.db.add(identifier, filelike)
        
    def _get_from_vault(self, identifier):
        return self.db.get(identifier)
 
    def exists(self, identifier):
        return self.db.exists(identifier)
    

class S3StorageVault(StorageVault):
    ''' a s3 file storage (based on boto) implementation of StorageVault
    '''
    
    def __init__(self):
        self.read_key_id = settings.STORAGE_VAULT_OPTIONS['read_auth_id']
        self.read_key_secret = settings.STORAGE_VAULT_OPTIONS['read_auth_secret']
        self.write_key_id  = settings.STORAGE_VAULT_OPTIONS['write_auth_id']
        self.write_key_secret = settings.STORAGE_VAULT_OPTIONS['write_auth_secret']
        raise NotImplementedError

    def _add_to_vault(self, identifier, filelike):
        raise NotImplementedError
        
    def _get_from_vault(self, identifier):
        raise NotImplementedError
