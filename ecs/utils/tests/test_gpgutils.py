import os, tempfile
from django.conf import settings
from ecs.utils.testcases import EcsTestCase
from ecs.utils.gpgutils import encrypt_sign, decrypt_verify


class Gpgutilstest(EcsTestCase):
    '''Tests for the gpgutils module
    
    Tests for data encryption, decryption and signature verification.
    '''
    
    def setUp(self):
        super(Gpgutilstest, self).setUp()
        self.gpghome = settings.STORAGE_VAULT['gpghome']
        self.encryption_uid = settings.STORAGE_VAULT['encryption_uid']
        self.signature_uid = settings.STORAGE_VAULT['signature_uid']
        
    def testConsistency(self):
        '''Tests if data can be encrypted and signed and then if it can be decrypted and verified via gpg and that it matches the previously encrypted test data.'''
        
        self.testdata=b"im very happy to be testdata"

        osdescriptor, encryptedfilename = tempfile.mkstemp()
        os.close(osdescriptor)

        try:
            with tempfile.TemporaryFile() as inputfile:
                inputfile.write(self.testdata)
                inputfile.seek(0)
                encrypt_sign(inputfile, encryptedfilename, self.gpghome,
                    self.encryption_uid, self.signature_uid)

            decryptedfile = decrypt_verify(encryptedfilename,
                self.gpghome, self.encryption_uid, self.signature_uid)

            self.assertNotEqual(self.testdata, open(encryptedfilename, 'rb').read())
            self.assertEqual(self.testdata, decryptedfile.read())
        finally:
            if os.path.exists(encryptedfilename):
                os.remove(encryptedfilename)
