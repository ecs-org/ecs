'''
Created on Aug 26, 2010

@author: amir
'''

from ecs.mediaserver.cacheable import Cacheable
from ecs.utils import pdfutils
from StringIO import StringIO

class PdfDocument(Cacheable):
    '''
 
    '''
    numpages=None
    def __init__(self, **kwargs):
        super(PdfDocument,self).__init__(**kwargs)
    
    def validate(self):
        data = self.getData()
        iodata = StringIO(data)
        pdfutils.pdf_isvalid(iodata)
        print "pages"
        self.numpages = pdfutils.pdf_pages(iodata)
        
