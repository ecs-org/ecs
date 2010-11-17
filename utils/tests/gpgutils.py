# -*- coding: utf-8 -*-

import os, tempfile
from django.conf import settings
from ecs.utils.testcases import EcsTestCase
from ecs.utils.gpgutils import encrypt_sign, decrypt_verify

class Gpgutilstest(EcsTestCase):
    testdata="im very happy to be testdata"        
    
    def testConsistency(self):
        inputfilename = encryptedfilename = decryptedfilename = None
        try:
            
            with tempfile.NamedTemporaryFile(delete=False) as inputfile:
                inputfilename = inputfile.name
                inputfile.write(self.testdata)
            osdescriptor, encryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)
            osdescriptor, decryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)
                
            encrypt_sign(inputfilename, encryptedfilename, settings.STORAGE_ENCRYPT ['gpghome'], settings.STORAGE_ENCRYPT ["owner"]) 
            decrypt_verify(encryptedfilename, decryptedfilename, settings.STORAGE_DECRYPT ['gpghome'], settings.STORAGE_DECRYPT ["owner"])
            
            self.assertEqual(self.testdata, open(inputfilename).read())
            self.assertNotEqual(self.testdata, open(encryptedfilename).read())
            self.assertEqual(self.testdata, open(decryptedfilename).read())
        
        finally:
            for i in inputfilename, encryptedfilename, decryptedfilename:
                if i is not None and os.path.exists(i):
                    os.remove(i)
