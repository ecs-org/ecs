import os

from django.test import TestCase
from ecs.mediaserver.renderer import Renderer
from django_extensions.utils.uuid import uuid4
from ecs.utils.pdfutils import pdf_pages

class RendererTest(TestCase):
    pdfdoc = 'test-pdf-14-seitig.pdf'

    def setUp(self):
        self.uuid = uuid4().get_hex();
        self.renderer = Renderer();
        self.f_pdfdoc = open(self.pdfdoc, "rb")
        self.pages = pdf_pages(self.f_pdfdoc)

    def test_Consistency(self):
        tiles = [ 1, 3, 5 ]
        width = [ 800, 768 ] 
            
        for t in tiles:
            for w in width:
                for docshots, data in self.renderer.renderPDFMontage(self.uuid, self.f_pdfdoc, w, t, t):
                    fullpages, remainder = divmod(t**2, self.pages)
                    if remainder > 0: 
                        fullpages =  fullpages + 1
                    self.assertEquals(len(docshots), fullpages);

        #TODO test png validity

    def __fillStore(self):
        pass
