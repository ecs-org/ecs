import os

from django_extensions.utils.uuid import uuid4

from ecs.utils.testcases import EcsTestCase
from ecs.utils.pdfutils import pdf_pages
from ecs.mediaserver.renderer import renderPDFMontage
import binascii

class RendererTest(EcsTestCase):
    pdfdoc = os.path.join(os.path.dirname(__file__), 'test-pdf-14-seitig.pdf')

    def setUp(self):
        self.uuid = uuid4().get_hex();
        self.f_pdfdoc = open(self.pdfdoc, "rb")
        self.pages = pdf_pages(self.f_pdfdoc)

    def testPngRendering(self):
        tiles = [ 1, 3, 5 ]
        width = [ 800, 768 ] 
        
        
        for t in tiles:
            for w in width:
                pagenum = 0
                for docshots, data in renderPDFMontage(self.uuid, self.pdfdoc, w, t, t):
                    pagenum += 1                    
                    # check for png magic
                    magic = binascii.a2b_hex('89504E470D0A1A0A')
                    offset = data.read(8).find(magic, 0)
                    self.assertEquals(offset, 0);
            
                # check for consistent page numbers
                fullpages, remainder = divmod(self.pages, t**2)
                if remainder > 0: 
                    fullpages =  fullpages + 1
                self.assertEquals(pagenum, fullpages);

