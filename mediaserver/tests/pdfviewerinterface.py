'''
Created on Sep 24, 2010

@author: amir
'''
import binascii
import urlparse
import os
import tempfile
from uuid import UUID,uuid4

from django.conf import settings

from ecs.utils import gpgutils, s3utils
from ecs.mediaserver.documentprovider import DocumentProvider
from ecs.mediaserver.cacheobjects import MediaBlob,Docshot
from ecs.utils.testcases import LoginTestCase
from django.core.urlresolvers import reverse
from django.http import HttpResponse

class PdfViewerInterface(LoginTestCase):
    pdfdoc = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig.pdf')
    png_magic = binascii.a2b_hex('89504E470D0A1A0A')
    pdf_magc = binascii.a2b_hex('25504446')
    
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
        # don't use the static instance, since we want to slip in test settings
        self.docprovider = DocumentProvider()

        with open(self.pdfdoc,"rb") as f_doc:
            encrypted = gpgutils.encrypt(f_doc, settings.MEDIASERVER_KEYOWNER)
            self.docprovider.addBlob(self.docblob, encrypted)
    
        self.docprovider.getBlob(self.docblob)

    def testExpiringDocshot(self):
        dsdata = self.docprovider.createDocshotData(self.docblob)

        for shot in dsdata:
            # simulate behavjour of ecs.mediaserver.views.docshot since the server isn't running
            url = shot['url']
            self.assertTrue(s3utils.verifyExpiringUrlString(url))
                
            parsed = urlparse.urlparse(url)
            print parsed.path
            _, uuid, tileset, width, pagenr, _ = parsed.path.rsplit('/', 5)
            tx, ty = tileset.split('x')

            ds = Docshot(MediaBlob(UUID(uuid)), tx, ty, width, pagenr)
            with self.docprovider.getDocshot(ds) as f:
                self.assertTrue(f.read(8) == self.png_magic);            

    def testViews(self):
        response = self.client.get(reverse('ecs.mediaserver.views.download_pdf', kwargs={'uuid': self.docblob.cacheID()}))
        self.failUnlessEqual(response.status_code, 200)
        
        print response.content.splitlines()[0]

