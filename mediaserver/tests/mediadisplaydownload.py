# -*- coding: utf-8 -*-
import os
import uuid

from ecs.utils.testcases import EcsTestCase

from ecs.mediaserver.utils import MediaProvider
from ecs.mediaserver.client import generate_media_url


class MediaDisplayDownload(EcsTestCase):
    '''Tests for the MediaProvider module
    
    Tests for the capabilities of the system for displaying media and providing download links for media.
    '''
    
    filename = 'menschenrechtserklaerung.pdf'
    pdfdocname = os.path.join(os.path.dirname(__file__), filename)
    
    def setUp(self):
        super(MediaDisplayDownload, self).setUp()
        self.mediaprovider = MediaProvider()
        self.identifier = uuid.uuid4().get_hex()
        
        with open(self.pdfdocname, "rb") as input:
            self.pdfdata = input.read()
            input.seek(0)
            self.mediaprovider.add_blob(self.identifier, input)

    def testPdfDownload(self):
        '''Tests that the produced download links for pdf documents by the system are correct
        and also tests that the data of the source documents matches the data of the pdf files that then reside in the system.
        '''
        
        fullurl = generate_media_url(self.identifier, self.filename, 'application/pdf', None, False)
        response = self.client.get(fullurl)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue(self.pdfdata, response.content)
