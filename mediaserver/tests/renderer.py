import os
import binascii
import tempfile
import shutil

from django.conf import settings
from uuid import uuid4

from ecs.utils.testcases import EcsTestCase
from ecs.utils.pdfutils import pdf_page_count, Page
from ecs.mediaserver.renderer import render_pages


class RendererTest(EcsTestCase):
    
    png_magic = binascii.a2b_hex('89504E470D0A1A0A')
    
    def setUp(self):
        super(RendererTest, self).setUp()
        self.uuid = uuid4().get_hex();
        self.pdfdoc = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig.pdf')    
        self.f_pdfdoc = open(self.pdfdoc, "rb")
        self.pages = pdf_page_count(self.f_pdfdoc)
        self.render_dirname = tempfile.mkdtemp()
    
    def tearDown(self):
        super(RendererTest, self).tearDown()
        # shutil.rmtree(self.render_dirname)
        
    def testPngRendering(self):
        tiles = settings.MS_SHARED ["tiles"]
        resolutions = settings.MS_SHARED ["resolutions"]
        
        pages_expected = []
        for t in tiles:
            for w in resolutions:
                tilepages = self.pages / (t*t)
                if self.pages % (t*t) > 0: tilepages += 1
                for p in range(1, tilepages+1):
                    pages_expected += [Page(self.uuid, t, t, w, p)]

        pages_real = []
        
        for page, data in render_pages(self.uuid, self.f_pdfdoc, self.render_dirname):
            # check for png magic
            current_magic = data.read(len(self.png_magic))
            self.assertTrue(current_magic == self.png_magic)
            if hasattr(data, "close"):
                data.close()
            pages_real += [page]
        
        self.assertEqual(len(pages_expected), len(pages_real))
        
