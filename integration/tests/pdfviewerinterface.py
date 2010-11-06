# -*- coding: utf-8 -*-

import os
import tempfile
import binascii
import urlparse
import uuid

from django.conf import settings
from django.core.urlresolvers import reverse

from ecs.mediaserver import documentprovider
from ecs.mediaserver.cacheobjects import MediaBlob, Docshot

from ecs.utils import gpgutils, s3utils, msutils, pdfutils
from ecs.utils.testcases import LoginTestCase


class PdfViewerInterface(LoginTestCase):
    pdfdoc = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig.pdf')
    png_magic = binascii.a2b_hex('89504E470D0A1A0A')
    pdf_magc = binascii.a2b_hex('25504446')
    docprovider = documentprovider.DocumentProvider()

    def setUp(self):
        super(PdfViewerInterface, self).setUp()

        self.docblob = MediaBlob(uuid.uuid4());
        with open(self.pdfdoc, "rb") as input:
            self.pages = pdfutils.pdf_pages(input)
        osdescriptor, encryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)

        gpgutils.encrypt(self.pdfdoc, encryptedfilename, settings.STORAGE_ENCRYPT ['gpghome'], settings.STORAGE_ENCRYPT ["owner"])
        with open(encryptedfilename, "rb") as encrypted:
            self.docprovider.addBlob(self.docblob, encrypted)

    def testExpiringDocshot(self):
        dsdata = msutils.generate_mediaurls(self.docblob.cacheID(), self.pages)
        key_id = settings.MS_CLIENT ["key_id"]
        key_secret = settings.MS_CLIENT ["key_secret"]
        
        for shot in dsdata:
            url = shot['url']
            self.assertTrue(s3utils.s3url(key_id, key_secret).verifyUrlString(url))
                            
            parsed = urlparse.urlparse(url)
            print parsed.path
            _, uuid, tileset, width, pagenr, _ = parsed.path.rsplit('/', 5)
            tx, ty = tileset.split('x')

            ds = Docshot(self.docblob, tx, ty, width, pagenr)
            with self.docprovider.getDocshot(ds) as f:
                current_magic = f.read(8)
                print (current_magic)
                self.assertTrue(current_magic == self.png_magic);

    def testPdfDownload(self):
        response = self.client.get(reverse('ecs.mediaserver.views.download_pdf', kwargs={'uuid': self.docblob.cacheID()}))
        self.failUnlessEqual(response.status_code, 200)

        print response.content.splitlines()[0]

