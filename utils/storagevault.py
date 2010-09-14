'''
Created on Aug 19, 2010

@author: amir
'''


from django.conf import settings
from ecs.utils.diskbuckets import DiskBuckets


def getVault():
    if settings.STORAGE_VAULT == 'ecs.utils.storagevault.LocalFileStorageVault':
        return LocalFileStorageVault()
    else:
        return UnimplementedStorageVault()
    # FIXME: this should look at settings.STORAGE_VAULT and use the settings there, but for now we hardcode it
    # return somethinglike getclassofstr(settings.STORAGE_VAULT)
    
class UnimplementedStorageVault():
    def __init__(self):
        raise UnimplementedError
 
    def add(self, uuid, filelike):
        raise UnimplementedError

    def get(self, uuid):
        raise UnimplementedError

    def exists(self, uuid):
        raise UnimplementedError

class LocalFileStorageVault(DiskBuckets):
    def __init__(self):
        rootdir = settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir']        
        super(LocalFileStorageVault, self).__init__(rootdir)

class S3StorageVault():
    def __init__(self):
        self.id = settings.STORAGE_VAULT_OPTIONS['authid']
        self.key = settings.STORAGE_VAULT_OPTIONS['authkey']
        raise UnimplementedError
 
    def add(self, uuid, filelike):
        raise UnimplementedError

    def get(self, uuid):
        raise UnimplementedError

    def exists(self, uuid):
        raise UnimplementedError

        