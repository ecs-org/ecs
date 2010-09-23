'''
Created on Aug 19, 2010

@author: amir
'''


from django.conf import settings
from ecs.utils.diskbuckets import DiskBuckets

def getVault():
    vault_path = settings.STORAGE_VAULT.split('.')
    vault_module = __import__('.'.join(vault_path[:-1]), fromlist=vault_path[:-2])
    vault = getattr(vault_module, vault_path[-1])
            
    if vault is None:
        raise KeyError("No Vault implementation for name: %s" % (settings.STORAGE_VAULT))
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

        
