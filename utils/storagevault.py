# -*- coding: utf-8 -*-

from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from ecs.utils.diskbuckets import DiskBuckets

def getVault():
    module, class_name = settings.STORAGE_VAULT.rsplit('.', 1)
    try:
        vault = getattr(import_module(module), class_name)
    except ImportError:
        raise ImproperlyConfigured("No Vault implementation for name: %s" % (settings.STORAGE_VAULT))
    return vault()

class LocalFileStorageVault(DiskBuckets):
    def __init__(self):
        rootdir = settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']        
        super(LocalFileStorageVault, self).__init__(rootdir)
    
    def create_or_update(self, identifier, filelike):
        raise NotImplementedError   # StorageVault does not allow update

    def purge(self, indentifier):
        raise NotImplementedError   # StorageVault does not allow purge

class S3StorageVault():
    def __init__(self):
        self.key_id = settings.STORAGE_VAULT_OPTIONS['key_id']
        self.key_secret = settings.STORAGE_VAULT_OPTIONS['key_secret']
        raise NotImplementedError
 
    def add(self, identifier, filelike):    
        raise NotImplementedError

    def get(self, identifier):
        raise NotImplementedError

    def exists(self, identifier):
        raise NotImplementedError
