'''
Created on Sep 24, 2010

@author: elchaschab
'''
import os
from uuid import uuid4
from ecs.utils.testcases import EcsTestCase
from ecs.utils.storagevault import getVault
from django.conf import settings
import tempfile
from ecs.utils import gpgutils
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.cacheobjects import MediaBlob
import urllib2
import binascii

class PdfViewerInterface(EcsTestCase):
    pdfdoc = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig.pdf')

    def setUp(self):
        # rewrite vault settings for testing
        tmpVaultDir = tempfile.mkdtemp()
        tmpRenderMemDir = tempfile.mkdtemp()
        tmpRenderDiskDir = tempfile.mkdtemp();

        settings.STORAGE_VAULT='ecs.utils.storagevault.LocalFileStorageVault'
        settings.STORAGE_VAULT_OPTIONS['LocalFileStorageVault.rootdir'] = tmpVaultDir
        settings.DOC_DISKCACHE = tmpRenderMemDir
        settings.RENDER_DISKCACHE = tmpRenderDiskDir
        settings.RENDER_MEMCACHE_LIB  = 'mockcache'

        self.docblob = MediaBlob(uuid4());
        # don't use the static instance, since we want it to slip in test settings
        self.docprovider = DocumentProvider()

        with open(self.pdfdoc,"rb") as f_doc:
            encrypted = gpgutils.encrypt(f_doc, settings.MEDIASERVER_KEYOWNER)
            self.docprovider.addBlob(self.docblob, encrypted)
    
        self.docprovider.getBlob(self.docblob)

    def testDocshot(self):
        dsdict = self.docprovider.createDocshotDictionary(self.docblob)

        for url in dsdict.values():
            # download and verify its (probably) a png
            with urllib2.urlopen(url) as png_in:        
                png_magic = binascii.a2b_hex('89504E470D0A1A0A')
                self.assertTrue(png_in.read(8) == png_magic);
        
            