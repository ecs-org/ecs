'''
Created on Sep 17, 2010

@author: elchaschab
'''
from django.test.testcases import TestCase
from ecs.utils.gpgutils import encrypt, decrypt
from django.conf import settings

class Gpgutilstest(TestCase):
    testdata="im very happy to be testdata"        
    
    def testConsistency(self):        
        encrypted = encrypt(self.testdata, settings.DOCUMENTS_GPG_HOME, settings.MEDIASERVER_KEYOWNER)
        decrypted = decrypt(encrypted, settings.MEDIASERVER_GPG_HOME, settings.MEDIASERVER_KEYOWNER)
        self.assertEqual(self.testdata, decrypted.read());
