'''
Created on Aug 19, 2010

@author: elchaschab
'''
import uuid
import unittest
import shutil
import hashlib

from ecs.mediaserver.diskbuckets import DiskBuckets

class TestDiskBuckets(unittest.TestCase):
    ROOT_DIR="/tmp/diskbuckets"

    def setUp(self):
        self.store = DiskBuckets(TestDiskBuckets.ROOT_DIR, 4, True); 
        for i in range(0, 10):
            self.uuids[i]=uuid.uuid4() 

        for u in self.uuids: 
            self.store.add(u, hashlib.md5(u).hexdigest())

           
    
    def tearDown(self):
        shutil.rmtree(TestDiskBuckets.ROOT_DIR)


    
    def testConsistency(self):

        for u in self.uuids: 
            self.assertEquals(self.store.get(u), hashlib.md5(u).hexdigest())

    def __fillStore(self):
        pass
    
if __name__ == "__main__":
    unittest.main()