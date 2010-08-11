# -*- coding: utf-8 -*-

import os
from ecs.utils.pdfutils import pdf_isvalid, pdf_pages
#import pyPdf


class Analyzer(object):
    def sniff(self, pdf_name):
        f = file(pdf_name, 'rb')
        self.sniff_file(f)
        f.close()

    def sniff_file(self, f):
        self.valid = False
        self.pages = 0
        self.valid = pdf_isvalid(f)
        if self.valid:
            self.pages = pdf_pages(f)
            