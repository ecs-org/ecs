'''
Created on Sep 17, 2010

@author: elchaschab
'''
from django.test.testcases import TestCase
from ecs.utils.gpgutils import encrypt, decrypt

class gpgutilstest(TestCase):
    testdata="im very happy to be testdata"        
    
    def testConsistency(self):
        encrypted = encrypt(self.testdata, self.testfingerprint);
        decrypted = decrypt(encrypted, self.testfingerprint);
        self.assertEqual(self.testdata, decrypted);
