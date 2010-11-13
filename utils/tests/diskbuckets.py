# -*- coding: utf-8 -*-

import uuid
import shutil
import hashlib
import tempfile

from ecs.utils.testcases import EcsTestCase
from ecs.utils.diskbuckets import DiskBuckets


class DiskBucketsTest(EcsTestCase):
 
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
