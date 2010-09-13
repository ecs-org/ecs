'''
Created on Aug 19, 2010

@author: amir
'''


from django.conf import settings
from ecs.utils.diskbuckets import DiskBuckets

class StorageVault(DiskBuckets):
    
    def __init__(self):
        self.id = settings.STORAGE_VAULT_OPTIONS['authid']
        self.key = settings.STORAGE_VAULT_OPTIONS['authkey']
        rootdir = settings.STORAGE_VAULT_OPTIONS['DiskBuckets.rootdir']        
        super(StorageVault.self).__init__(rootdir)
