'''
Created on Sep 24, 2010

@author: elchaschab
'''
import binascii
import urlparse
import re
import os
import tempfile
from uuid import UUID,uuid4

from django.conf import settings

from ecs.utils import gpgutils, s3utils
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.cacheobjects import MediaBlob,Docshot
from ecs.utils.testcases import EcsTestCase
from ecs.utils.storagevault import getVault


class PdfViewerInterface(EcsTestCase):
    pdfdoc = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig.pdf')
    png_magic = binascii.a2b_hex('89504E470D0A1A0A')

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
        dsdata = self.docprovider.createDocshotData(self.docblob)

        for shot in dsdata:
            # simulate behavjour of ecs.mediaserver.views.docshot since the server isn't running
            url = shot['url']
            self.assertTrue(s3utils.verifyExpiringUrlString(url))
                
            parsed = urlparse.urlparse(url)
            _, uuid, tileset, width, pagenr = parsed.path.split('/')
            tx, ty = tileset.split('x')

            ds = Docshot(uuid, tx, ty, width, pagenr)
            with self.docprovider.getDocshot(ds) as f:
                png_magic = binascii.a2b_hex('89504E470D0A1A0A')
                self.assertTrue(f.read(8) == png_magic);            

