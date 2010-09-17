'''
Created on Aug 19, 2010

@author: elchaschab
'''
import uuid
import unittest
import shutil
import hashlib
import tempfile
from django.test import TestCase
from ecs.utils.diskbuckets import DiskBuckets

class DiskBucketsTest(TestCase):
 
    def setUp(self):
        self.root_dir = tempfile.mkdtemp()
        self.store = DiskBuckets(self.root_dir, 4, True)
        self.uuids = []
        for i in range(0, 10):
            self.uuids.append(uuid.uuid4().get_hex())

        for u in self.uuids: 
            self.store.add(u, hashlib.md5(u).hexdigest())

    def tearDown(self):
        shutil.rmtree(self.root_dir)
    
    def testConsistency(self):
        
        for u in self.uuids: 
            self.assertEquals(self.store.get(u).read(), hashlib.md5(u).hexdigest())

    def __fillStore(self):
        pass
    
if __name__ == "__main__":
    unittest.main()