# -*- coding: utf-8 -*-

import uuid
import shutil
import hashlib
import tempfile
import StringIO


from ecs.utils.testcases import EcsTestCase
from ecs.mediaserver.diskbuckets import DiskBuckets
from ecs.mediaserver.storagevault import getVault


class StorageVaultTest(EcsTestCase):
 
    def setUp(self):
        self.vault = getVault()
        self.uuids = []
        for i in range(0, 10):
            self.uuids.append(uuid.uuid4().get_hex())

        for u in self.uuids: 
            self.vault.add(u, StringIO.StringIO(hashlib.md5(u).hexdigest()))
    
    def testConsistency(self):
        
        for u in self.uuids: 
            filelike_fromvault = self.vault.get(u)
            data_fromvault = filelike_fromvault.read()
            self.vault.decommission(filelike_fromvault)
            
            self.assertEquals(data_fromvault, hashlib.md5(u).hexdigest())
