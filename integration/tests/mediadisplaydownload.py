# -*- coding: utf-8 -*-

import os
import tempfile
import binascii
import urlparse
import uuid

from time import time

from django.conf import settings
from django.core.urlresolvers import reverse


from ecs.utils.testcases import LoginTestCase
from ecs.utils import gpgutils, s3utils, msutils, pdfutils
from ecs.mediaserver.utils import MediaProvider


class MediaDisplayDownload(LoginTestCase):
    filename = 'menschenrechtserklaerung.pdf'
    pdfdocname = os.path.join(os.path.dirname(__file__), filename)
    png_magic = binascii.a2b_hex('89504E470D0A1A0A')
    mediaprovider = MediaProvider()

    def setUp(self):
        super(MediaDisplayDownload, self).setUp()

        self.identifier = uuid.uuid4().get_hex()
        with open(self.pdfdocname, "rb") as input:
            self.pages = pdfutils.pdf_page_count(input)
            input.seek(0)
            self.pdfdata = input.read()
        osdescriptor, encryptedfilename = tempfile.mkstemp(); os.close(osdescriptor)

        gpgutils.encrypt_sign(self.pdfdocname, encryptedfilename, 
            settings.STORAGE_ENCRYPT ['gpghome'], settings.STORAGE_ENCRYPT ["owner"])
        with open(encryptedfilename, "rb") as encrypted:
            self.mediaprovider._addBlob(self.identifier, encrypted)
        os.remove(encryptedfilename)

    def testPdfPages(self):
        dsdata = msutils.generate_pages_urllist(self.identifier, self.pages)
        key_id = settings.MS_CLIENT ["key_id"]
        key_secret = settings.MS_CLIENT ["key_secret"]
        
        for shot in dsdata:
            url = shot['url']
            self.assertTrue(s3utils.S3url(key_id, key_secret).verifyUrlString(url))
            
            parsed = urlparse.urlparse(url)
            dummy, uuid, tileset, width, pagenr, dummy = parsed.path.rsplit('/', 5)
            tx, ty = tileset.split('x')

            ds = pdfutils.Page(self.identifier, tx, ty, width, pagenr)
            with self.mediaprovider.getPage(ds) as f:
                current_magic = f.read(len(self.png_magic))
                self.assertTrue(current_magic == self.png_magic);

    def testPdfDownload(self):
        baseurl = ""
        bucket = reverse('ecs.mediaserver.views.get_pdf', kwargs={'uuid': self.identifier, 'filename': self.filename})
        expiration_sec = settings.MS_SHARED ["url_expiration_sec"]
        expires = int(time()) + expiration_sec
        key_id = settings.MS_CLIENT ["key_id"]
        key_secret = settings.MS_CLIENT ["key_secret"]
        fullurl = s3utils.S3url(key_id, key_secret).createUrl(baseurl, bucket, '', key_id, expires)
        response = self.client.get(fullurl)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(self.pdfdata, response.content)
        
