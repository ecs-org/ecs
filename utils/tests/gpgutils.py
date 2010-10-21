'''
Created on Sep 17, 2010

@author: elchaschab
'''
from django.test.testcases import TestCase
from ecs.utils.gpgutils import encrypt, decrypt

class Gpgutilstest(TestCase):
    testdata="im very happy to be testdata"        
    
    def testConsistency(self):
        encrypted = encrypt(self.testdata, "mediaserver");
        decrypted = decrypt(encrypted, "mediaserver");
        self.assertEqual(self.testdata, decrypted.read());
