# -*- coding: utf-8 -*-

import os
import binascii
import urlparse
import uuid

from django.conf import settings

from ecs.utils.testcases import EcsTestCase
from ecs.utils import pdfutils

from ecs.mediaserver.utils import MediaProvider, AuthUrl
from ecs.mediaserver.client import generate_pages_urllist, generate_media_url


class MediaDisplayDownload(EcsTestCase):
    '''Tests for the MediaProvider and AuthUrl module
    
    Tests for the capabilities of the system for displaying media and providing download links for media.
    '''
    
    filename = 'menschenrechtserklaerung.pdf'
    pdfdocname = os.path.join(os.path.dirname(__file__), filename)
    png_magic = binascii.a2b_hex('89504E470D0A1A0A')
    
    def setUp(self):
        super(MediaDisplayDownload, self).setUp()
        self.mediaprovider = MediaProvider()
        self.identifier = uuid.uuid4().get_hex()
        
        with open(self.pdfdocname, "rb") as input:
            self.pages = pdfutils.pdf_page_count(input)
            self.pdfdata = input.read()
            input.seek(0)
            self.mediaprovider.add_blob(self.identifier, input)

    def testPdfPages(self):
        '''Tests that pages rendered as png images are valid png images
        and that the urls generated for viewing single pdf pages as png images are correct.
        '''
        
        dsdata = generate_pages_urllist(self.identifier, self.pages)
        key_id = settings.MS_CLIENT ["key_id"]
        key_secret = settings.MS_CLIENT ["key_secret"]
        
        for shot in dsdata:
            url = shot['url']
            self.assertTrue(AuthUrl(key_id, key_secret).verify(url))
            
            parsed = urlparse.urlparse(url)
            dummy, uuid, tileset, width, pagenr, dummy = parsed.path.rsplit('/', 5)
            tx, ty = tileset.split('x')

            ds = pdfutils.Page(self.identifier, tx, ty, width, pagenr)
            with self.mediaprovider.get_page(ds) as f:
                current_magic = f.read(len(self.png_magic))
                self.assertTrue(current_magic == self.png_magic);

    def testPdfDownload(self):
        '''Tests that the produced download links for pdf documents by the system are correct
        and also tests that the data of the source documents matches the data of the pdf files that then reside in the system.
        '''
        
        fullurl = generate_media_url(self.identifier, self.filename, 'application/pdf', None, False)
        response = self.client.get(fullurl)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(self.pdfdata, response.content)
