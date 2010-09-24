'''
Created on Aug 19, 2010

@author: amir
'''

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

class S3StorageVault():
    def __init__(self):
        self.id = settings.STORAGE_VAULT_OPTIONS['authid']
        self.key = settings.STORAGE_VAULT_OPTIONS['authkey']
        raise NotImplementedError
 
    def add(self, uuid, filelike):
        raise NotImplementedError

    def get(self, uuid):
        raise NotImplementedError

    def exists(self, uuid):
        raise NotImplementedError

        
