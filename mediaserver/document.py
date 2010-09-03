'''
Created on Aug 26, 2010

@author: amir
'''

from ecs.mediaserver.cacheable import Cacheable
from ecs.utils import pdfutils

class PdfDocument(Cacheable):
    '''
 
    '''
    numpages=None
    def __init__(self, **kwargs):
        super(PdfDocument,self).__init__(**kwargs)
    
    def validate(self):
        data = self.getData()
        pdfutils.pdf_isvalid(data)
        self.numpages = pdfutils.pdf_pages(data)
        