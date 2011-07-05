# -*- coding: utf-8 -*-

import os, tempfile
from django.conf import settings
from ecs.utils.testcases import EcsTestCase
from ecs.utils.gpgutils import encrypt_sign, decrypt_verify, reset_keystore, gen_keypair, import_key

class Gpgutilstest(EcsTestCase):
    def setUp(self):
        super(Gpgutilstest, self).setUp()
        
        self.encrypt_gpghome = settings.STORAGE_ENCRYPT ['gpghome']
        self.encrypt_owner = settings.STORAGE_ENCRYPT['encrypt_owner']
        self.signing_owner = settings.STORAGE_ENCRYPT['signing_owner']
        
        self.decrypt_gpghome = settings.STORAGE_DECRYPT ['gpghome']
        self.decrypt_owner = settings.STORAGE_DECRYPT['decrypt_owner']
        self.verify_owner = settings.STORAGE_DECRYPT['verify_owner'] 


    def fresh_temporary_entities(self):
        self.testdir = tempfile.mkdtemp()
        self.authority_name = "ecs_authority"
        self.mediaserver_name = "ecs_mediaserver"
        
        # create encrypt gpghome and set encrypt signing owner
        self.encrypt_gpghome = os.path.join(self.testdir, self.authority_name)
        self.encrypt_owner = self.mediaserver_name
        self.signing_owner = self.authority_name
        os.mkdir(self.encrypt_gpghome)
        
        # create decrypt gpghome and set decrypt verify owner
        self.decrypt_gpghome= os.path.join(self.testdir, self.mediaserver_name)
        self.decrypt_owner = self.mediaserver_name
        self.verify_owner = self.authority_name
        os.mkdir(self.decrypt_gpghome)
        
        # generate keypair files for authority
        auth_sec_name = os.path.join(self.testdir, self.authority_name+".sec")
        auth_pub_name = os.path.join(self.testdir, self.authority_name+".pub")
        gen_keypair(self.authority_name, auth_sec_name, auth_pub_name)
        
        # generate keypair files for mediaserver
        ms_sec_name = os.path.join(self.testdir, self.mediaserver_name+".sec")
        ms_pub_name = os.path.join(self.testdir, self.mediaserver_name+".pub")
        gen_keypair(self.mediaserver_name, ms_sec_name, ms_pub_name)

        # import secretkey of authority and public key of mediaserver to authority        
        import_key(auth_sec_name, self.encrypt_gpghome)
        import_key(ms_pub_name, self.encrypt_gpghome)
        
        # import secretkey of mediaserver and public key of authority to mediaserver
        import_key(ms_sec_name, self.decrypt_gpghome)
        import_key(auth_pub_name, self.decrypt_gpghome)


    def testConsistency(self):
        # self.fresh_temporary_entities()
        self.testdata="im very happy to be testdata"

        inputfilename = encryptedfilename = decryptedfilename = None
        try:
            
            with tempfile.NamedTemporaryFile(delete=False) as inputfile:
                inputfilename = inputfile.name
                inputfile.write(self.testdata)
            osdescriptor, encryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)
            osdescriptor, decryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)
                
            encrypt_sign(inputfilename, encryptedfilename, self.encrypt_gpghome, self.encrypt_owner, self.signing_owner)
            decrypt_verify(encryptedfilename, decryptedfilename, self.decrypt_gpghome, self.decrypt_owner, self.verify_owner)
            
            self.assertEqual(self.testdata, open(inputfilename).read())
            self.assertNotEqual(self.testdata, open(encryptedfilename).read())
            self.assertEqual(self.testdata, open(decryptedfilename).read())
        
        finally:
            for i in inputfilename, encryptedfilename, decryptedfilename:
                if i is not None and os.path.exists(i):
                    os.remove(i)
    
    def testError(self):
        pass
        
    def testFail(self):
        pass
